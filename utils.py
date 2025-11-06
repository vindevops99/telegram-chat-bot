import os
import urllib.parse
from dotenv import load_dotenv

# Nạp biến môi trường từ .env (nếu chạy local)
load_dotenv()

# Config tài khoản VietQR (đọc từ env, có default dự phòng)
BANK_CODE = os.getenv("BANK_CODE", "MB")
ACCOUNT_NUMBER = os.getenv("BANK_ACCOUNT", "2040108383002")

def generate_qr(amount, phone, service):
    """
    Trả về URL QR VietQR với nội dung chuyển khoản:
    'SĐT khách hàng - Tên dịch vụ'
    """
    qr_note = f"{phone} - {service}"   # chỉ dùng SĐT - dịch vụ
    qr_note_encoded = urllib.parse.quote(qr_note)
    qr_url = f"https://img.vietqr.io/image/{BANK_CODE}-{ACCOUNT_NUMBER}-compact2.png?amount={amount}&addInfo={qr_note_encoded}"
    return qr_url

