#!/usr/bin/env python3
"""
기술 블로그 크롤링 및 AI 요약 시스템
매일 실행되어 주요 기술 블로그의 최신 글을 수집하고 AI로 요약합니다.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Any

from crawler import TechBlogCrawler
from summarizer import AISummarizer
from notifier import SlackNotifier, TelegramNotifier
from config import BLOG_SOURCES, AI_CONFIG

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyTechCrawler:
    def __init__(self):
        self.crawler = TechBlogCrawler()
        self.summarizer = AISummarizer()
        self.slack_notifier = SlackNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.output_dir = Path("../../research/trends")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_daily_crawl(self):
        """일일 크롤링 실행"""
        logger.info("🚀 일일 기술 블로그 크롤링 시작")
        
        today = datetime.now().strftime("%Y-%m-%d")
        results = {
            "date": today,
            "blogs": {},
            "summary": "",
            "trending_topics": [],
            "total_articles": 0
        }
        
        try:
            # 1. 각 블로그에서 최신 글 수집
            for blog_name, blog_config in BLOG_SOURCES.items():
                logger.info(f"📰 {blog_name} 크롤링 중...")
                
                articles = await self.crawler.crawl_blog(
                    blog_name, 
                    blog_config,
                    days_back=1  # 어제부터 오늘까지
                )
                
                if articles:
                    # AI로 각 글 요약
                    summarized_articles = []
                    for article in articles:
                        summary = await self.summarizer.summarize_article(article)
                        summarized_articles.append({
                            **article,
                            "ai_summary": summary
                        })
                    
                    results["blogs"][blog_name] = {
                        "source_url": blog_config["url"],
                        "articles": summarized_articles,
                        "count": len(summarized_articles)
                    }
                    results["total_articles"] += len(summarized_articles)
                    
                    logger.info(f"✅ {blog_name}: {len(summarized_articles)}개 글 처리 완료")
                else:
                    logger.warning(f"⚠️ {blog_name}: 새로운 글이 없습니다")
            
            # 2. 전체 요약 및 트렌드 분석
            if results["total_articles"] > 0:
                logger.info("🤖 전체 요약 및 트렌드 분석 중...")
                
                all_articles = []
                for blog_data in results["blogs"].values():
                    all_articles.extend(blog_data["articles"])
                
                # 전체 요약 생성
                results["summary"] = await self.summarizer.generate_daily_summary(all_articles)
                
                # 트렌딩 토픽 추출
                results["trending_topics"] = await self.summarizer.extract_trending_topics(all_articles)
                
                # 3. 마크다운 파일로 저장
                await self.save_daily_report(results)
                
                # 4. 알림 발송
                await self.send_notifications(results)
                
                logger.info(f"🎉 일일 크롤링 완료: 총 {results['total_articles']}개 글 처리")
            else:
                logger.info("📭 오늘은 새로운 글이 없습니다")
                
        except Exception as e:
            logger.error(f"❌ 크롤링 중 오류 발생: {str(e)}")
            await self.send_error_notification(str(e))
            raise
    
    async def save_daily_report(self, results: Dict[str, Any]):
        """일일 리포트를 마크다운 파일로 저장"""
        today = results["date"]
        filename = f"daily-summary-{today}.md"
        filepath = self.output_dir / filename
        
        # 마크다운 내용 생성
        content = self.generate_markdown_report(results)
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 인덱스 파일 업데이트
        await self.update_index_file(today, results["total_articles"])
        
        logger.info(f"💾 리포트 저장 완료: {filepath}")
    
    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """마크다운 리포트 생성"""
        content = f"""# 기술 블로그 일일 요약 - {results['date']} 📰

> AI가 자동으로 수집하고 요약한 오늘의 주요 기술 소식

## 📊 요약 통계

- **총 수집 글 수**: {results['total_articles']}개
- **수집 블로그**: {len(results['blogs'])}개
- **생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔥 오늘의 트렌딩 토픽

"""
        
        for i, topic in enumerate(results['trending_topics'], 1):
            content += f"{i}. **{topic['topic']}** ({topic['count']}회 언급)\n"
            content += f"   - {topic['description']}\n\n"
        
        content += f"""## 📝 전체 요약

{results['summary']}

---

## 📚 블로그별 상세 내용

"""
        
        for blog_name, blog_data in results['blogs'].items():
            content += f"""### {blog_name} ({blog_data['count']}개 글)

**출처**: [{blog_name}]({blog_data['source_url']})

"""
            
            for article in blog_data['articles']:
                content += f"""#### [{article['title']}]({article['url']})

**작성일**: {article.get('published_date', 'N/A')}  
**작성자**: {article.get('author', 'N/A')}

**AI 요약**:
{article['ai_summary']}

**주요 키워드**: {', '.join(article.get('keywords', []))}

---

"""
        
        content += f"""## 🏷️ 태그

`#기술블로그` `#일일요약` `#AI요약` `#자동화` `#{results['date'].replace('-', '')}`

---

*이 문서는 AI가 자동으로 생성했습니다. 정확성을 위해 원문을 확인해주세요.*
"""
        
        return content
    
    async def update_index_file(self, date: str, article_count: int):
        """인덱스 파일 업데이트"""
        index_file = self.output_dir / "README.md"
        
        # 기존 인덱스 파일 읽기 또는 새로 생성
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = """# 기술 블로그 트렌드 분석 📈

> AI가 매일 수집하고 분석하는 주요 기술 블로그 동향

## 📅 일일 요약 목록

"""
        
        # 새로운 엔트리 추가
        new_entry = f"- [{date}](daily-summary-{date}.md) - {article_count}개 글 수집\n"
        
        # 날짜 순으로 정렬하여 삽입
        lines = content.split('\n')
        insert_index = -1
        for i, line in enumerate(lines):
            if line.startswith('- [') and date > line[3:13]:
                insert_index = i
                break
        
        if insert_index == -1:
            # 맨 끝에 추가
            content += new_entry
        else:
            # 적절한 위치에 삽입
            lines.insert(insert_index, new_entry.strip())
            content = '\n'.join(lines)
        
        # 파일 저장
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    async def send_notifications(self, results: Dict[str, Any]):
        """알림 발송"""
        message = f"""📰 오늘의 기술 블로그 요약 완료!

📅 날짜: {results['date']}
📊 수집 글 수: {results['total_articles']}개
🔥 트렌딩 토픽: {len(results['trending_topics'])}개

주요 토픽:
{chr(10).join([f"• {topic['topic']}" for topic in results['trending_topics'][:3]])}

자세한 내용은 GitHub에서 확인하세요!
"""
        
        # Slack 알림
        await self.slack_notifier.send_message(message)
        
        # Telegram 알림
        await self.telegram_notifier.send_message(message)
    
    async def send_error_notification(self, error_msg: str):
        """오류 알림 발송"""
        message = f"❌ 기술 블로그 크롤링 중 오류 발생:\n\n{error_msg}"
        
        await self.slack_notifier.send_message(message)
        await self.telegram_notifier.send_message(message)

async def main():
    """메인 실행 함수"""
    crawler = DailyTechCrawler()
    await crawler.run_daily_crawl()

if __name__ == "__main__":
    asyncio.run(main()) 