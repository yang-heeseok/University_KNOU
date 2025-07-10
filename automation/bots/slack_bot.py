"""
Slack 봇 구현
학습 진행 상황과 기술 블로그 요약을 Slack으로 알림
"""

import os
import json
import asyncio
from datetime import datetime
from slack_sdk.webhook import WebhookClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel = os.getenv("SLACK_CHANNEL", "#tech-updates")
        
        if self.webhook_url:
            self.webhook_client = WebhookClient(self.webhook_url)
        
        if self.bot_token:
            self.client = WebClient(token=self.bot_token)
    
    async def send_webhook_message(self, message: str, title: str = None, color: str = "good"):
        """웹훅을 통한 메시지 전송"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL이 설정되지 않았습니다")
            return False
        
        try:
            blocks = self._create_message_blocks(message, title, color)
            
            response = self.webhook_client.send(
                text=title or "학습 아카이브 알림",
                blocks=blocks
            )
            
            logger.info(f"Slack 웹훅 메시지 전송 성공: {response.status_code}")
            return True
            
        except Exception as e:
            logger.error(f"Slack 웹훅 메시지 전송 실패: {str(e)}")
            return False
    
    async def send_bot_message(self, message: str, title: str = None, color: str = "good"):
        """봇 토큰을 통한 메시지 전송"""
        if not self.bot_token:
            logger.warning("Slack bot token이 설정되지 않았습니다")
            return False
        
        try:
            blocks = self._create_message_blocks(message, title, color)
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=title or "학습 아카이브 알림",
                blocks=blocks
            )
            
            logger.info(f"Slack 봇 메시지 전송 성공: {response['ts']}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack 봇 메시지 전송 실패: {e.response['error']}")
            return False
    
    def _create_message_blocks(self, message: str, title: str = None, color: str = "good"):
        """Slack 메시지 블록 생성"""
        blocks = []
        
        # 헤더 블록
        if title:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            })
        
        # 메시지 블록
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        })
        
        # 구분선
        blocks.append({"type": "divider"})
        
        # 푸터
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🤖 자동 생성 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        return blocks
    
    async def send_daily_summary_notification(self, summary_data: dict):
        """일일 요약 알림 전송"""
        title = f"📰 기술 블로그 일일 요약 - {summary_data['date']}"
        
        message = f"""
*📊 오늘의 수집 현황*
• 총 수집 글 수: *{summary_data['total_articles']}개*
• 수집 블로그: *{len(summary_data['blogs'])}개*
• 트렌딩 토픽: *{len(summary_data['trending_topics'])}개*

*🔥 주요 트렌딩 토픽*
"""
        
        for i, topic in enumerate(summary_data['trending_topics'][:5], 1):
            message += f"{i}. *{topic['topic']}* ({topic['count']}회 언급)\n"
        
        message += f"""
*📚 블로그별 수집 현황*
"""
        
        for blog_name, blog_data in summary_data['blogs'].items():
            message += f"• {blog_name}: {blog_data['count']}개 글\n"
        
        message += f"""
<https://github.com/your-username/University_KNOU/tree/main/research/trends|📖 자세한 내용 보기>
"""
        
        return await self.send_webhook_message(message, title, "good")
    
    async def send_deployment_notification(self, deployment_info: dict):
        """배포 완료 알림 전송"""
        title = "🚀 학습 아카이브 배포 완료"
        
        message = f"""
*📝 변경사항*
{deployment_info.get('commit_message', 'N/A')}

*👤 작성자*
{deployment_info.get('author', 'N/A')}

*🔗 배포된 사이트*
<{deployment_info.get('site_url', '#')}|학습 아카이브 보기>

*⏰ 배포 시간*
{deployment_info.get('deploy_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
"""
        
        return await self.send_webhook_message(message, title, "good")
    
    async def send_error_notification(self, error_info: dict):
        """오류 알림 전송"""
        title = "❌ 시스템 오류 발생"
        
        message = f"""
*🚨 오류 유형*
{error_info.get('error_type', 'Unknown Error')}

*📝 오류 메시지*
```
{error_info.get('error_message', 'No details available')}
```

*📍 발생 위치*
{error_info.get('location', 'Unknown')}

*⏰ 발생 시간*
{error_info.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

*🔧 조치 필요*
관리자 확인이 필요합니다.
"""
        
        return await self.send_webhook_message(message, title, "danger")
    
    async def send_study_progress_notification(self, progress_data: dict):
        """학습 진행 상황 알림 전송"""
        title = f"📚 학습 진행 상황 - {progress_data.get('subject', 'Unknown')}"
        
        message = f"""
*📖 과목명*
{progress_data.get('subject', 'N/A')}

*📊 진행률*
{progress_data.get('progress', 0)}% 완료

*✅ 완료된 내용*
"""
        
        for item in progress_data.get('completed_items', []):
            message += f"• {item}\n"
        
        message += f"""
*📋 다음 할 일*
"""
        
        for item in progress_data.get('next_items', []):
            message += f"• {item}\n"
        
        message += f"""
*🎯 이번 주 목표*
{progress_data.get('weekly_goal', 'N/A')}
"""
        
        return await self.send_webhook_message(message, title, "good")

# 사용 예시
async def main():
    bot = SlackBot()
    
    # 테스트 메시지
    await bot.send_webhook_message(
        "테스트 메시지입니다! 🎉",
        "Slack 봇 테스트",
        "good"
    )

if __name__ == "__main__":
    asyncio.run(main()) 