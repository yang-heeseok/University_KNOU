# 자동화 시스템 설정 가이드 🤖

## 📋 개요

이 자동화 시스템은 다음 기능들을 제공합니다:

1. **GitHub Pages 자동 배포** - main 브랜치 push 시 정적 사이트 배포
2. **일일 기술 블로그 크롤링** - AI 기반 요약 및 트렌드 분석
3. **Slack/Telegram 봇 알림** - 실시간 학습 진행 상황 및 시스템 알림

---

## 🚀 빠른 시작

### 1단계: 환경 변수 설정

GitHub Repository Settings > Secrets and variables > Actions에서 다음 환경 변수들을 설정하세요:

#### 필수 설정

```bash
# AI API 키
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...

# Slack 설정
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#tech-updates

# Telegram 설정
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ADMIN_CHAT_ID=987654321
```

### 2단계: GitHub Pages 활성화

1. Repository Settings > Pages
2. Source: "GitHub Actions" 선택
3. 첫 번째 push 후 자동으로 사이트가 배포됩니다

### 3단계: 워크플로우 활성화

-   `.github/workflows/` 폴더의 워크플로우들이 자동으로 활성화됩니다
-   Actions 탭에서 실행 상태를 확인할 수 있습니다

---

## 🔧 상세 설정

### 📖 정적 사이트 배포 설정

#### 빌드 스크립트 커스터마이징

`package.json`에 다음 스크립트를 추가하세요:

```json
{
	"scripts": {
		"build:docs": "node scripts/build-docs.js",
		"generate:index": "node scripts/generate-index.js"
	},
	"devDependencies": {
		"markdown-it": "^13.0.1",
		"fs-extra": "^11.1.1",
		"glob": "^10.3.10"
	}
}
```

#### 테마 및 스타일 설정

`docs/` 폴더에 CSS 파일을 추가하여 사이트 스타일을 커스터마이징할 수 있습니다:

```css
/* docs/style.css */
:root {
	--primary-color: #2563eb;
	--secondary-color: #64748b;
	--background-color: #f8fafc;
}

body {
	font-family: 'Inter', sans-serif;
	background-color: var(--background-color);
}
```

### 🤖 크롤러 설정

#### 블로그 소스 추가/수정

`automation/crawler/config.py`에서 크롤링할 블로그를 설정할 수 있습니다:

```python
BLOG_SOURCES = {
    "새로운 블로그": {
        "url": "https://example.com/blog",
        "type": "custom",
        "rss_feed": "https://example.com/feed",
        "selectors": {
            "title": ".post-title",
            "content": ".post-content",
            "author": ".author",
            "date": ".date"
        },
        "language": "ko",
        "description": "블로그 설명"
    }
}
```

#### AI 요약 설정

```python
# 요약 길이 및 스타일 조정
SUMMARY_CONFIG = {
    "max_summary_length": 300,  # 글자 수
    "keywords_count": 5,        # 키워드 개수
    "summary_language": "ko",   # 요약 언어
    "include_code_snippets": True,
    "extract_technical_terms": True
}
```

#### 크롤링 스케줄 변경

`.github/workflows/daily-crawler.yml`에서 스케줄을 수정할 수 있습니다:

```yaml
on:
    schedule:
        # 매일 오후 2시 (UTC 5시)로 변경
        - cron: '0 5 * * *'
```

### 🤖 봇 설정

#### Slack 봇 설정

1. **Slack App 생성**

    - https://api.slack.com/apps 에서 새 앱 생성
    - Bot Token Scopes: `chat:write`, `chat:write.public`

2. **Webhook URL 생성**

    - Incoming Webhooks 활성화
    - 채널 선택 후 Webhook URL 복사

3. **커스텀 메시지 형식**

```python
# automation/bots/slack_bot.py 수정
def _create_custom_message_blocks(self, data):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{data['title']}*\n{data['content']}"
            },
            "accessory": {
                "type": "image",
                "image_url": data.get('image_url', ''),
                "alt_text": "thumbnail"
            }
        }
    ]
```

#### Telegram 봇 설정

1. **봇 생성**

    - @BotFather에게 `/newbot` 명령어 전송
    - 봇 이름과 username 설정
    - Bot Token 받기

2. **Chat ID 확인**

    ```bash
    # 봇에게 메시지 보낸 후 실행
    curl https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
    ```

3. **명령어 커스터마이징**

```python
# automation/bots/telegram_bot.py에 새 명령어 추가
async def custom_command(self, update: Update, context):
    """커스텀 명령어"""
    message = "커스텀 응답 메시지"
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# 핸들러 등록
self.application.add_handler(CommandHandler("custom", self.custom_command))
```

---

## 📊 모니터링 및 로그

### GitHub Actions 로그 확인

1. Repository > Actions 탭
2. 워크플로우 실행 내역 확인
3. 실패한 작업의 상세 로그 확인

### 봇 상태 모니터링

#### Slack 봇 상태 확인

```bash
curl -X POST -H 'Authorization: Bearer xoxb-your-token' \
-H 'Content-type: application/json' \
--data '{"channel":"#tech-updates","text":"봇 상태 테스트"}' \
https://slack.com/api/chat.postMessage
```

#### Telegram 봇 상태 확인

```bash
curl https://api.telegram.org/bot<BOT_TOKEN>/getMe
```

### 로그 레벨 설정

```python
# automation/crawler/main.py
import logging

# 로그 레벨 변경 (DEBUG, INFO, WARNING, ERROR)
logging.basicConfig(level=logging.DEBUG)
```

---

## 🔒 보안 설정

### API 키 보안

1. **GitHub Secrets 사용**: 절대 코드에 직접 API 키를 포함하지 마세요
2. **권한 최소화**: 필요한 최소 권한만 부여
3. **정기적 갱신**: API 키를 정기적으로 갱신

### 봇 보안

```python
# 허용된 사용자만 명령어 사용 가능하도록 설정
ALLOWED_USERS = [123456789, 987654321]  # Telegram User ID

async def check_user_permission(self, user_id):
    return user_id in ALLOWED_USERS
```

---

## 🛠️ 트러블슈팅

### 자주 발생하는 문제들

#### 1. GitHub Actions 실패

```bash
# 로그 확인 방법
1. Actions 탭 > 실패한 워크플로우 클릭
2. 실패한 단계의 로그 확인
3. 환경 변수 설정 확인
```

#### 2. 크롤링 실패

```python
# 디버그 모드로 실행
cd automation/crawler
python -c "
import asyncio
from main import DailyTechCrawler
crawler = DailyTechCrawler()
asyncio.run(crawler.run_daily_crawl())
"
```

#### 3. 봇 응답 없음

```bash
# Telegram 봇 상태 확인
curl https://api.telegram.org/bot<TOKEN>/getMe

# Slack 봇 권한 확인
# Slack App 설정에서 OAuth & Permissions 확인
```

### 로그 파일 위치

```
automation/
├── logs/
│   ├── crawler.log
│   ├── slack_bot.log
│   └── telegram_bot.log
```

---

## 📈 성능 최적화

### 크롤링 성능 향상

```python
# automation/crawler/config.py
CRAWLER_CONFIG = {
    "max_concurrent_requests": 10,  # 동시 요청 수
    "delay_between_requests": 0.5,  # 요청 간 지연 (초)
    "timeout": 15,                  # 타임아웃 (초)
    "retry_attempts": 2             # 재시도 횟수
}
```

### AI 요약 최적화

```python
# 배치 처리로 API 호출 최적화
async def batch_summarize(self, articles, batch_size=5):
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        await self.process_batch(batch)
```

---

## 🔄 업데이트 및 유지보수

### 정기 업데이트 체크리스트

-   [ ] 의존성 패키지 업데이트
-   [ ] API 키 갱신
-   [ ] 크롤링 대상 사이트 구조 변경 확인
-   [ ] 봇 명령어 및 기능 개선
-   [ ] 로그 파일 정리

### 백업 설정

```bash
# 중요 데이터 백업 스크립트
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz research/ automation/config/
```

---

## 📞 지원 및 문의

-   **GitHub Issues**: 버그 리포트 및 기능 요청
-   **Discussions**: 사용법 문의 및 아이디어 공유
-   **Wiki**: 상세한 설정 가이드 및 FAQ

---

**마지막 업데이트**: 2024년 현재  
**버전**: 1.0.0
