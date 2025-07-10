"""
기술 블로그 크롤러 모듈
지난 24시간 동안 발행된 컨텐츠를 대상으로 크롤링을 수행합니다.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path
import hashlib
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class TechBlogCrawler:
    def __init__(self):
        self.session = None
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def crawl_blog(self, blog_name: str, blog_config: dict, days_back: int = 1):
        """
        특정 블로그에서 지난 N일 동안의 글을 크롤링합니다.
        
        Args:
            blog_name: 블로그 이름
            blog_config: 블로그 설정 정보
            days_back: 크롤링할 일수 (기본값: 1일)
        
        Returns:
            List[dict]: 크롤링된 글 정보 리스트
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        articles = []
        
        try:
            if blog_config.get("rss_feed"):
                articles = await self._crawl_from_rss(blog_name, blog_config, cutoff_date)
            elif blog_config.get("api_endpoint"):
                articles = await self._crawl_from_api(blog_name, blog_config, cutoff_date)
            else:
                articles = await self._crawl_from_html(blog_name, blog_config, cutoff_date)
            
            # 중복 제거 및 검증
            articles = self._deduplicate_articles(articles)
            articles = self._validate_articles(articles, cutoff_date)
            
            logger.info(f"{blog_name}: {len(articles)}개 글 수집 (지난 {days_back}일)")
            
        except Exception as e:
            logger.error(f"{blog_name} 크롤링 실패: {str(e)}")
            
        return articles

    async def _crawl_from_rss(self, blog_name: str, config: dict, cutoff_date: datetime):
        """RSS 피드에서 크롤링"""
        articles = []
        
        try:
            async with self.session.get(config["rss_feed"]) as response:
                rss_content = await response.text()
                
            feed = feedparser.parse(rss_content)
            
            for entry in feed.entries:
                # 발행 날짜 확인
                published_date = self._parse_date(entry.get('published'))
                if not published_date or published_date < cutoff_date:
                    continue
                
                # 기본 정보 추출
                article = {
                    "title": entry.get('title', '').strip(),
                    "url": entry.get('link', ''),
                    "published_date": published_date.isoformat(),
                    "author": entry.get('author', ''),
                    "summary": entry.get('summary', ''),
                    "source": blog_name,
                    "language": config.get("language", "en")
                }
                
                # 전체 컨텐츠 가져오기
                full_content = await self._get_full_content(article["url"], config)
                if full_content:
                    article["content"] = full_content
                    article["keywords"] = self._extract_keywords(full_content)
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"RSS 크롤링 실패 ({blog_name}): {str(e)}")
            
        return articles

    async def _crawl_from_api(self, blog_name: str, config: dict, cutoff_date: datetime):
        """API에서 크롤링"""
        articles = []
        
        try:
            # API별 특별 처리
            if blog_name == "Dev.to":
                articles = await self._crawl_devto_api(config, cutoff_date)
            elif blog_name == "네이버 D2":
                articles = await self._crawl_naver_d2_api(config, cutoff_date)
            
        except Exception as e:
            logger.error(f"API 크롤링 실패 ({blog_name}): {str(e)}")
            
        return articles

    async def _crawl_devto_api(self, config: dict, cutoff_date: datetime):
        """Dev.to API 크롤링"""
        articles = []
        
        # 최신 글 가져오기
        url = f"{config['api_endpoint']}?per_page=50&top=1"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
        for item in data:
            published_date = self._parse_date(item.get('published_at'))
            if not published_date or published_date < cutoff_date:
                continue
                
            article = {
                "title": item.get('title', ''),
                "url": item.get('url', ''),
                "published_date": published_date.isoformat(),
                "author": item.get('user', {}).get('name', ''),
                "summary": item.get('description', ''),
                "content": await self._get_full_content(item.get('url'), config),
                "tags": item.get('tag_list', []),
                "source": "Dev.to",
                "language": "en"
            }
            
            article["keywords"] = self._extract_keywords(article.get("content", ""))
            articles.append(article)
            
        return articles

    async def _crawl_from_html(self, blog_name: str, config: dict, cutoff_date: datetime):
        """HTML 파싱으로 크롤링"""
        articles = []
        
        try:
            async with self.session.get(config["url"]) as response:
                html_content = await response.text()
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 블로그별 특별 처리
            if blog_name == "Hacker News":
                articles = await self._crawl_hackernews(soup, config, cutoff_date)
            else:
                articles = await self._crawl_generic_html(soup, config, cutoff_date, blog_name)
                
        except Exception as e:
            logger.error(f"HTML 크롤링 실패 ({blog_name}): {str(e)}")
            
        return articles

    async def _crawl_hackernews(self, soup: BeautifulSoup, config: dict, cutoff_date: datetime):
        """Hacker News 특별 처리"""
        articles = []
        
        # Hacker News의 경우 RSS를 사용하는 것이 더 효율적
        return await self._crawl_from_rss("Hacker News", config, cutoff_date)

    async def _get_full_content(self, url: str, config: dict, max_length: int = 5000):
        """글의 전체 컨텐츠 가져오기"""
        if not url:
            return ""
            
        try:
            # 캐시 확인
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.txt"
            
            if cache_file.exists():
                return cache_file.read_text(encoding='utf-8')
            
            async with self.session.get(url) as response:
                html_content = await response.text()
                
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 컨텐츠 추출 (블로그별 셀렉터 사용)
            content_selectors = config.get("selectors", {}).get("content", ["article", ".content", ".post-content"])
            if isinstance(content_selectors, str):
                content_selectors = [content_selectors]
                
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            # 길이 제한
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            # 캐시 저장
            cache_file.write_text(content, encoding='utf-8')
            
            return content
            
        except Exception as e:
            logger.error(f"컨텐츠 가져오기 실패 ({url}): {str(e)}")
            return ""

    def _parse_date(self, date_str):
        """다양한 날짜 형식 파싱"""
        if not date_str:
            return None
            
        try:
            # RFC 2822 형식 (RSS에서 일반적)
            if date_str.count(',') == 1:
                return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
            
            # ISO 8601 형식
            if 'T' in date_str:
                # 타임존 정보 제거
                date_str = date_str.split('+')[0].split('Z')[0]
                return datetime.fromisoformat(date_str)
                
            # 기타 형식들
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"날짜 파싱 실패: {date_str} - {str(e)}")
            
        return None

    def _extract_keywords(self, content: str, max_keywords: int = 10):
        """간단한 키워드 추출"""
        if not content:
            return []
            
        # 기술 관련 키워드 패턴
        tech_patterns = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js',
            'ai', 'machine learning', 'deep learning', 'data science',
            'cloud', 'aws', 'azure', 'docker', 'kubernetes',
            'blockchain', 'cryptocurrency', 'web3',
            'api', 'rest', 'graphql', 'microservices',
            'database', 'sql', 'nosql', 'mongodb',
            'frontend', 'backend', 'fullstack',
            'mobile', 'ios', 'android', 'flutter',
            'devops', 'ci/cd', 'automation'
        ]
        
        content_lower = content.lower()
        found_keywords = []
        
        for pattern in tech_patterns:
            if pattern in content_lower:
                found_keywords.append(pattern)
                
        return found_keywords[:max_keywords]

    def _deduplicate_articles(self, articles):
        """중복 글 제거"""
        seen_urls = set()
        deduplicated = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(article)
                
        return deduplicated

    def _validate_articles(self, articles, cutoff_date: datetime):
        """글 검증 및 필터링"""
        validated = []
        
        for article in articles:
            # 필수 필드 확인
            if not article.get('title') or not article.get('url'):
                continue
                
            # 컨텐츠 최소 길이 확인
            content = article.get('content', '')
            if len(content) < 100:  # 너무 짧은 글 제외
                continue
                
            # 날짜 재확인
            published_date = self._parse_date(article.get('published_date'))
            if published_date and published_date < cutoff_date:
                continue
                
            validated.append(article)
            
        return validated

    async def save_crawling_results(self, results: dict, output_dir: Path):
        """크롤링 결과를 GitHub에 저장"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 날짜별 폴더 생성
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = output_dir / today
        daily_dir.mkdir(exist_ok=True)
        
        # 1. 전체 결과를 JSON으로 저장
        json_file = daily_dir / "crawling_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 2. 블로그별 개별 파일 저장
        for blog_name, blog_data in results.get('blogs', {}).items():
            blog_file = daily_dir / f"{blog_name.replace(' ', '_')}.json"
            with open(blog_file, 'w', encoding='utf-8') as f:
                json.dump(blog_data, f, ensure_ascii=False, indent=2)
        
        # 3. 인덱스 파일 업데이트
        await self._update_crawling_index(output_dir, today, results)
        
        logger.info(f"크롤링 결과 저장 완료: {daily_dir}")

    async def _update_crawling_index(self, output_dir: Path, date: str, results: dict):
        """크롤링 인덱스 파일 업데이트"""
        index_file = output_dir / "index.json"
        
        # 기존 인덱스 로드
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"crawling_history": [], "statistics": {}}
        
        # 새로운 엔트리 추가
        new_entry = {
            "date": date,
            "total_articles": results.get('total_articles', 0),
            "blogs_crawled": len(results.get('blogs', {})),
            "trending_topics": len(results.get('trending_topics', [])),
            "timestamp": datetime.now().isoformat()
        }
        
        # 중복 제거 후 추가
        index_data["crawling_history"] = [
            entry for entry in index_data["crawling_history"] 
            if entry["date"] != date
        ]
        index_data["crawling_history"].append(new_entry)
        
        # 최근 30일만 유지
        index_data["crawling_history"] = sorted(
            index_data["crawling_history"], 
            key=lambda x: x["date"], 
            reverse=True
        )[:30]
        
        # 통계 업데이트
        index_data["statistics"] = {
            "total_crawls": len(index_data["crawling_history"]),
            "total_articles_collected": sum(entry["total_articles"] for entry in index_data["crawling_history"]),
            "last_updated": datetime.now().isoformat()
        }
        
        # 저장
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2) 