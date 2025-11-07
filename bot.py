# bot.py - Fixed & Improved Version
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import logging
from config import Config
from handlers import start, echo, get_inbill_handler, get_expense_handler, get_report_handler
from db import init_db

# Logging với format đầy đủ hơn
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    handlers=[
        logging.FileHandler(Config.LOG_FILE),  # Lưu log vào file
        logging.StreamHandler()  # In ra console
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Hàm main khởi động bot"""
    
    # Validate cấu hình
    if not Config.validate():
        logger.error("❌ Cấu hình không hợp lệ! Vui lòng kiểm tra file .env")
        return
    
    # Khởi tạo application
    # Initialize DB (create file and tables if needed)
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return

    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    # Handler /start
    app.add_handler(CommandHandler("start", start))
    
    # Handler /inbill (ConversationHandler) - BÂY GIỜ ĐÃ CHỨA CALLBACK
    app.add_handler(get_inbill_handler())
    
    # Handler /expense (ConversationHandler) - BÂY GIỜ ĐÃ CHỨA CALLBACK
    app.add_handler(get_expense_handler())
    
    # Handler /report (ConversationHandler) - BÂY GIỜ ĐÃ CHỨA CALLBACK
    app.add_handler(get_report_handler())
    
    # Handler echo text (đặt cuối cùng để không conflict)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Thông báo khởi động
    logger.info("=" * 50)
    logger.info("🤖 Bot đang khởi động...")
    logger.info("=" * 50)
    
    try:
        # Chạy bot
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"❌ Lỗi khi chạy bot: {e}")
    finally:
        logger.info("🛑 Bot đã dừng.")

if __name__ == "__main__":
    main()
