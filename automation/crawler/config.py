"""
기술 블로그 크롤러 설정
"""

import os

# AI 설정
AI_CONFIG = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "temperature": 0.3
    },
    "claude": {
        "api_key": os.getenv("CLAUDE_API_KEY"),
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1000,
        "temperature": 0.3
    }
}

# 알림 설정
NOTIFICATION_CONFIG = {
    "slack": {
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
        "channel": "#tech-updates",
        "username": "TechCrawler Bot"
    },
    "telegram": {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID")
    }
}

# 블로그 소스 설정
BLOG_SOURCES = {
    # 영어 기술 블로그
    "Hacker News": {
        "url": "https://news.ycombinator.com/",
        "type": "hackernews",
        "rss_feed": "https://hnrss.org/frontpage",
        "selectors": {
            "title": ".titleline > a",
            "url": ".titleline > a",
            "score": ".score",
            "comments": ".subtext a[href*='item']"
        },
        "language": "en",
        "description": "개발자 커뮤니티의 핫한 소식"
    },
    
    "Dev.to": {
        "url": "https://dev.to/",
        "type": "devto",
        "api_endpoint": "https://dev.to/api/articles",
        "selectors": {
            "title": "h1",
            "content": ".crayons-article__main",
            "author": ".crayons-story__secondary .crayons-link",
            "tags": ".crayons-tag"
        },
        "language": "en",
        "description": "개발자 블로그 플랫폼"
    },
    
    "Medium Engineering": {
        "url": "https://medium.engineering/",
        "type": "medium",
        "rss_feed": "https://medium.com/feed/engineering-at-meta",
        "selectors": {
            "title": "h1",
            "content": "article section",
            "author": ".author-name",
            "claps": ".claps-count"
        },
        "language": "en",
        "description": "Medium의 엔지니어링 블로그"
    },
    
    # 한국 기술 블로그
    "카카오 기술블로그": {
        "url": "https://tech.kakao.com/",
        "type": "kakao",
        "rss_feed": "https://tech.kakao.com/feed/",
        "selectors": {
            "title": ".post-title",
            "content": ".post-content",
            "author": ".post-author",
            "date": ".post-date"
        },
        "language": "ko",
        "description": "카카오의 기술 및 서비스 소개"
    },
    
    "우아한형제들 기술블로그": {
        "url": "https://techblog.woowahan.com/",
        "type": "woowahan",
        "rss_feed": "https://techblog.woowahan.com/feed/",
        "selectors": {
            "title": ".entry-title",
            "content": ".entry-content",
            "author": ".author-name",
            "category": ".category"
        },
        "language": "ko",
        "description": "배달의민족 기술 블로그"
    },
    
    "네이버 D2": {
        "url": "https://d2.naver.com/",
        "type": "naver_d2",
        "api_endpoint": "https://d2.naver.com/api/v1/contents",
        "selectors": {
            "title": ".post_title",
            "content": ".post_content",
            "author": ".post_author",
            "tags": ".post_tag"
        },
        "language": "ko",
        "description": "네이버의 기술 및 서비스 소개"
    }
}

# 크롤링 설정
CRAWLER_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "timeout": 30,
    "max_retries": 3,
    "delay_between_requests": 1,  # 초
    "max_articles_per_blog": 10,
    "content_min_length": 100,  # 최소 컨텐츠 길이
}

# 요약 설정
SUMMARY_CONFIG = {
    "max_summary_length": 300,  # 글자 수
    "keywords_count": 5,
    "trending_topics_count": 10,
    "summary_language": "ko",  # 요약 언어
    "include_code_snippets": True,
    "extract_technical_terms": True
}

# 출력 설정
OUTPUT_CONFIG = {
    "base_dir": "../../research/trends",
    "daily_summary_template": "daily-summary-{date}.md",
    "index_file": "README.md",
    "backup_enabled": True,
    "backup_days": 30
} 