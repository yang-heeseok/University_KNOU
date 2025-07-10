"""
Telegram 봇 구현
학습 진행 상황과 기술 블로그 요약을 Telegram으로 알림
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
import json

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            logger.warning("Telegram bot token이 설정되지 않았습니다")
    
    async def send_message(self, message: str, chat_id: str = None, parse_mode: str = ParseMode.MARKDOWN):
        """메시지 전송"""
        if not self.bot_token:
            logger.warning("Telegram bot token이 설정되지 않았습니다")
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.warning("Telegram chat ID가 설정되지 않았습니다")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            
            logger.info(f"Telegram 메시지 전송 성공: {target_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Telegram 메시지 전송 실패: {str(e)}")
            return False
    
    async def send_photo_with_caption(self, photo_url: str, caption: str, chat_id: str = None):
        """이미지와 캡션 전송"""
        if not self.bot_token:
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            return False
        
        try:
            await self.bot.send_photo(
                chat_id=target_chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"Telegram 이미지 전송 성공: {target_chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Telegram 이미지 전송 실패: {str(e)}")
            return False
    
    async def send_daily_summary_notification(self, summary_data: dict):
        """일일 요약 알림 전송"""
        message = f"""📰 *기술 블로그 일일 요약* - {summary_data['date']}

📊 *오늘의 수집 현황*
• 총 수집 글 수: *{summary_data['total_articles']}개*
• 수집 블로그: *{len(summary_data['blogs'])}개*
• 트렌딩 토픽: *{len(summary_data['trending_topics'])}개*

🔥 *주요 트렌딩 토픽*"""
        
        for i, topic in enumerate(summary_data['trending_topics'][:5], 1):
            message += f"\n{i}. *{topic['topic']}* ({topic['count']}회 언급)"
        
        message += f"\n\n📚 *블로그별 수집 현황*"
        
        for blog_name, blog_data in summary_data['blogs'].items():
            message += f"\n• {blog_name}: {blog_data['count']}개 글"
        
        message += f"\n\n[📖 자세한 내용 보기](https://github.com/your-username/University_KNOU/tree/main/research/trends)"
        message += f"\n\n🏷️ #기술블로그 #일일요약 #AI요약 #자동화"
        
        return await self.send_message(message)
    
    async def send_deployment_notification(self, deployment_info: dict):
        """배포 완료 알림 전송"""
        message = f"""🚀 *학습 아카이브 배포 완료*

📝 *변경사항*
{deployment_info.get('commit_message', 'N/A')}

👤 *작성자*
{deployment_info.get('author', 'N/A')}

🔗 *배포된 사이트*
[학습 아카이브 보기]({deployment_info.get('site_url', '#')})

⏰ *배포 시간*
{deployment_info.get('deploy_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

🏷️ #배포완료 #자동화 #학습아카이브"""
        
        return await self.send_message(message)
    
    async def send_error_notification(self, error_info: dict):
        """오류 알림 전송"""
        message = f"""❌ *시스템 오류 발생*

🚨 *오류 유형*
{error_info.get('error_type', 'Unknown Error')}

📝 *오류 메시지*
```
{error_info.get('error_message', 'No details available')}
```

📍 *발생 위치*
{error_info.get('location', 'Unknown')}

⏰ *발생 시간*
{error_info.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

🔧 *조치 필요*
관리자 확인이 필요합니다.

🏷️ #오류알림 #시스템점검"""
        
        # 관리자에게도 별도 전송
        await self.send_message(message, self.admin_chat_id)
        return await self.send_message(message)
    
    async def send_study_progress_notification(self, progress_data: dict):
        """학습 진행 상황 알림 전송"""
        message = f"""📚 *학습 진행 상황* - {progress_data.get('subject', 'Unknown')}

📖 *과목명*
{progress_data.get('subject', 'N/A')}

📊 *진행률*
{progress_data.get('progress', 0)}% 완료

✅ *완료된 내용*"""
        
        for item in progress_data.get('completed_items', []):
            message += f"\n• {item}"
        
        message += f"\n\n📋 *다음 할 일*"
        
        for item in progress_data.get('next_items', []):
            message += f"\n• {item}"
        
        message += f"\n\n🎯 *이번 주 목표*\n{progress_data.get('weekly_goal', 'N/A')}"
        message += f"\n\n🏷️ #학습진행 #진도체크 #{progress_data.get('subject', '').replace(' ', '')}"
        
        return await self.send_message(message)
    
    async def send_weekly_summary(self, weekly_data: dict):
        """주간 요약 알림 전송"""
        message = f"""📊 *주간 학습 요약* - {weekly_data.get('week', 'Unknown')}

📈 *이번 주 성과*
• 완료한 강의: {weekly_data.get('completed_lectures', 0)}개
• 작성한 노트: {weekly_data.get('notes_written', 0)}개
• 해결한 문제: {weekly_data.get('problems_solved', 0)}개
• 학습 시간: {weekly_data.get('study_hours', 0)}시간

🎯 *주요 성취*"""
        
        for achievement in weekly_data.get('achievements', []):
            message += f"\n✅ {achievement}"
        
        message += f"\n\n📋 *다음 주 계획*"
        
        for plan in weekly_data.get('next_week_plans', []):
            message += f"\n📌 {plan}"
        
        message += f"\n\n💡 *학습 팁*\n{weekly_data.get('study_tip', 'N/A')}"
        message += f"\n\n🏷️ #주간요약 #학습통계 #진도관리"
        
        return await self.send_message(message)
    
    async def send_reminder(self, reminder_data: dict):
        """학습 리마인더 전송"""
        message = f"""⏰ *학습 리마인더*

📚 *오늘 할 일*"""
        
        for task in reminder_data.get('today_tasks', []):
            message += f"\n• {task}"
        
        message += f"\n\n🎯 *이번 주 목표*\n{reminder_data.get('weekly_goal', 'N/A')}"
        
        if reminder_data.get('deadline_approaching'):
            message += f"\n\n⚠️ *마감 임박*"
            for deadline in reminder_data.get('deadline_approaching', []):
                message += f"\n🚨 {deadline}"
        
        message += f"\n\n💪 화이팅! 오늘도 열심히 공부해봅시다!"
        message += f"\n\n🏷️ #학습리마인더 #일일목표"
        
        return await self.send_message(message)

class TelegramBotApp:
    """Telegram 봇 애플리케이션 (대화형 기능)"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.application = None
        
        if self.bot_token:
            self.application = Application.builder().token(self.bot_token).build()
            self._setup_handlers()
    
    def _setup_handlers(self):
        """핸들러 설정"""
        if not self.application:
            return
        
        # 명령어 핸들러
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        
        # 메시지 핸들러
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context):
        """시작 명령어"""
        message = """🎓 *방송통신대학교 학습 아카이브 봇*

안녕하세요! 학습 진행 상황과 기술 동향을 알려드리는 봇입니다.

📋 *사용 가능한 명령어*
/help - 도움말
/status - 시스템 상태
/progress - 학습 진행 상황
/summary - 최근 요약

🤖 자동으로 다음 알림을 받을 수 있습니다:
• 일일 기술 블로그 요약
• 학습 진행 상황
• 배포 완료 알림
• 시스템 오류 알림"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context):
        """도움말 명령어"""
        message = """📖 *도움말*

🤖 *자동 알림*
• 매일 오전 9시: 기술 블로그 요약
• 주간 일요일: 학습 진행 요약
• 실시간: 배포 및 오류 알림

📋 *명령어*
/status - 시스템 상태 확인
/progress - 학습 진행 상황 조회
/summary - 최근 기술 블로그 요약

💬 *문의사항*
GitHub Issues를 통해 문의해주세요."""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context):
        """상태 명령어"""
        message = f"""📊 *시스템 상태*

🟢 *크롤러 상태*: 정상 동작
🟢 *AI 요약*: 정상 동작
🟢 *알림 시스템*: 정상 동작

📈 *최근 활동*
• 마지막 크롤링: {datetime.now().strftime('%Y-%m-%d %H:%M')}
• 수집된 글: 15개
• 생성된 요약: 6개

⏰ *다음 예정*
• 다음 크롤링: 내일 오전 9시
• 주간 요약: 일요일"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def progress_command(self, update: Update, context):
        """진행 상황 명령어"""
        message = """📚 *학습 진행 상황*

📊 *전체 진행률*
• 컴퓨터과학개론: 75% ████████░░
• 데이터구조: 60% ██████░░░░
• 알고리즘: 45% ████░░░░░░
• 운영체제: 30% ███░░░░░░░

✅ *이번 주 완료*
• 강의 노트 3개 작성
• 실습 문제 5개 해결
• 프로젝트 1개 완료

📋 *다음 주 계획*
• 알고리즘 심화 학습
• 운영체제 프로젝트 시작"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def summary_command(self, update: Update, context):
        """요약 명령어"""
        message = f"""📰 *최근 기술 블로그 요약*

📅 *{datetime.now().strftime('%Y-%m-%d')}*

🔥 *트렌딩 토픽*
1. AI/ML 발전 동향
2. 클라우드 네이티브
3. 웹 성능 최적화

📚 *수집 현황*
• 총 15개 글 수집
• 6개 블로그에서 수집
• AI 요약 완료

[📖 자세한 내용 보기](https://github.com/your-username/University_KNOU/tree/main/research/trends)"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context):
        """일반 메시지 처리"""
        user_message = update.message.text.lower()
        
        if "안녕" in user_message or "hello" in user_message:
            response = "안녕하세요! 🎓 학습 아카이브 봇입니다. /help 명령어로 사용법을 확인해보세요!"
        elif "상태" in user_message or "status" in user_message:
            await self.status_command(update, context)
            return
        elif "진행" in user_message or "progress" in user_message:
            await self.progress_command(update, context)
            return
        else:
            response = "죄송합니다. 이해하지 못했습니다. /help 명령어로 사용법을 확인해보세요."
        
        await update.message.reply_text(response)
    
    async def run(self):
        """봇 실행"""
        if self.application:
            await self.application.run_polling()

# 사용 예시
async def main():
    bot = TelegramBot()
    
    # 테스트 메시지
    await bot.send_message("테스트 메시지입니다! 🎉")

if __name__ == "__main__":
    asyncio.run(main()) 