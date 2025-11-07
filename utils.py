"""
Utilities module - Các hàm tiện ích
"""
import urllib.parse
from typing import Optional
from config import Config
import logging

logger = logging.getLogger(__name__)


def generate_qr(amount: int, phone: str, service: str) -> str:
    """
    Trả về URL QR VietQR với nội dung chuyển khoản:
    'SĐT khách hàng - Tên dịch vụ'
    
    Args:
        amount: Số tiền cần thanh toán
        phone: Số điện thoại khách hàng
        service: Tên dịch vụ
    
    Returns:
        URL của QR code image
    
    Raises:
        ValueError: Nếu BANK_ACCOUNT chưa được cấu hình
    """
    if not Config.BANK_ACCOUNT:
        logger.error("BANK_ACCOUNT chưa được cấu hình")
        raise ValueError("BANK_ACCOUNT chưa được cấu hình trong file .env")
    
    qr_note = f"{phone} - {service}"   # chỉ dùng SĐT - dịch vụ
    qr_note_encoded = urllib.parse.quote(qr_note)
    qr_url = f"https://img.vietqr.io/image/{Config.BANK_CODE}-{Config.BANK_ACCOUNT}-compact2.png?amount={amount}&addInfo={qr_note_encoded}"
    return qr_url

