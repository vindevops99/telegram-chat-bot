# Telegram Expense Tracking Bot

Một bot Telegram giúp theo dõi chi tiêu và quản lý hóa đơn, được phát triển bằng Python.

## Demo

https://files.catbox.moe/03d545.mp4

Video demo trên cho thấy các tính năng chính của bot:
- Khởi động và menu chính
- Quy trình nhập hóa đơn mới
- Tạo báo cáo chi tiêu
- Xuất file CSV
- Tạo mã QR thanh toán

## Tính năng

- 📝 Ghi lại hóa đơn và chi tiêu
- 📊 Tạo báo cáo chi tiêu
- 💬 Tương tác thông qua các lệnh đơn giản
- 🗄️ Lưu trữ dữ liệu trong SQLite
- 📅 Xuất báo cáo theo định dạng CSV

## Yêu cầu hệ thống

- Python 3.8 hoặc cao hơn
- Docker (tùy chọn, nếu muốn chạy trong container)

## Cài đặt

### Cách 1: Cài đặt trực tiếp

1. Clone repository:
```bash
git clone https://github.com/vindevops99/list-opensource.git
cd telegram-chat-bot
```

2. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate  # Windows
```

3. Cài đặt các dependency:
```bash
pip install -r requirements.txt
```

4. Tạo file `.env` và cấu hình token:
```bash
BOT_TOKEN=your_telegram_bot_token_here
```

### Cách 2: Sử dụng Docker

1. Build Docker image:
```bash
docker-compose build
```

2. Chạy container:
```bash
docker-compose up -d
```

## Sử dụng

Bot hỗ trợ các lệnh sau:

- `/start` - Bắt đầu sử dụng bot
- `/inbill` - Ghi lại hóa đơn mới
- `/expense` - Ghi lại khoản chi tiêu
- `/report` - Tạo báo cáo chi tiêu
- `/cancel` - Hủy thao tác hiện tại
## Cấu trúc Project

```
telegram-chat-bot/
├── bot.py              # File chính để khởi động bot
├── handlers.py         # Xử lý các lệnh của bot
├── db.py              # Quản lý cơ sở dữ liệu
├── utils.py           # Các hàm tiện ích
├── requirements.txt    # Danh sách các dependency
├── docker-compose.yml # Cấu hình Docker Compose
├── Dockerfile         # Cấu hình Docker
└── entrypoint.sh      # Script khởi động cho Docker
```

## Dependencies chính

- python-telegram-bot==20.3
- python-dotenv>=1.0.0
- pandas==2.3.3
- pillow==12.0.0
- numpy==2.2.6

## Phát triển

1. Bot sử dụng thư viện `python-telegram-bot` phiên bản 20.3
2. Dữ liệu được lưu trữ trong SQLite database
3. Báo cáo được xuất ra dưới dạng file CSV trong thư mục `report/`

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

[MIT License](LICENSE)

## Tác giả

- **vindevops99** - *Initial work* - [GitHub](https://github.com/vindevops99)

Project được khởi tạo bởi [vindevops99](https://github.com/vindevops99/list-opensource)