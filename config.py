"""
Configuration module - Quản lý tất cả cấu hình của ứng dụng
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Class quản lý cấu hình ứng dụng"""
    
    # Telegram Bot
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    
    # Database
    DB_NAME: str = os.getenv("DB_NAME", "sales.db")
    
    # VietQR Bank Configuration
    BANK_CODE: str = os.getenv("BANK_CODE", "MB")
    BANK_ACCOUNT: Optional[str] = os.getenv("BANK_ACCOUNT")
    
    # Logging
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Timezone
    TIMEZONE_OFFSET_HOURS: int = int(os.getenv("TIMEZONE_OFFSET_HOURS", "7"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate các cấu hình bắt buộc
        Returns True nếu tất cả đều hợp lệ, False nếu thiếu
        """
        errors = []
        
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "YOUR_TOKEN_HERE":
            errors.append("BOT_TOKEN chưa được cấu hình")
        
        if not cls.BANK_ACCOUNT:
            logger.warning("BANK_ACCOUNT chưa được cấu hình - QR code có thể không hoạt động")
        
        if errors:
            for error in errors:
                logger.error(f"❌ Config Error: {error}")
            return False
        
        return True
    
    @classmethod
    def get_timezone_info(cls):
        """Lấy thông tin timezone"""
        from datetime import timezone, timedelta
        return timezone(timedelta(hours=cls.TIMEZONE_OFFSET_HOURS))

