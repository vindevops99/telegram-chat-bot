# 🤖 Telegram Sales & Expense Management Bot

Một bot Telegram giúp theo dõi doanh thu, chi tiêu và quản lý hóa đơn, được phát triển bằng Python với SQLite database.

## Demo

🎥 [Xem video demo tính năng của Telegram Chat Bot →](https://files.catbox.moe/03d545.mp4)

Video demo trên cho thấy các tính năng chính của bot:
- Khởi động và menu chính
- Quy trình nhập hóa đơn mới
- Tạo báo cáo chi tiêu
- Xuất file CSV
- Tạo mã QR thanh toán

## ✨ Tính năng

- 📝 **Quản lý hóa đơn**: Ghi lại thông tin khách hàng, dịch vụ, số tiền
- 💸 **Quản lý chi phí**: Theo dõi các khoản chi tiêu theo danh mục
- 📊 **Báo cáo tự động**: Tạo báo cáo theo tháng hiện tại, tháng trước hoặc khoảng thời gian tùy chỉnh
- 💳 **QR Code thanh toán**: Tự động tạo mã QR VietQR để khách hàng thanh toán
- 📄 **Xuất CSV**: Xuất báo cáo chi tiết ra file CSV
- 🗄️ **SQLite Database**: Lưu trữ dữ liệu an toàn và dễ backup
- 🎯 **Menu tương tác**: Giao diện thân thiện với inline keyboard

## 📋 Yêu cầu hệ thống

- **Python**: 3.10 hoặc cao hơn (khuyến nghị 3.10+)
- **Docker**: 20.10+ và Docker Compose 2.0+ (tùy chọn, nếu muốn chạy trong container)
- **Telegram Bot Token**: Lấy từ [@BotFather](https://t.me/botfather) trên Telegram

## Cài đặt

### Cách 1: Cài đặt trực tiếp

1. Clone repository:
```bash
git clone https://github.com/vindevops99/telegram-chat-bot.git
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

4. Tạo file `.env` và cấu hình các biến môi trường:
```bash
# Telegram Bot Token (BẮT BUỘC)
BOT_TOKEN=your_telegram_bot_token_here

# Database Configuration
DB_NAME=sales.db

# VietQR Bank Configuration (Tùy chọn - để tạo QR code)
BANK_CODE=MB
BANK_ACCOUNT=your_bank_account_number_here

# Logging Configuration (Tùy chọn)
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Timezone Configuration (Tùy chọn)
TIMEZONE_OFFSET_HOURS=7
```

> 💡 **Lưu ý**: Bạn có thể copy từ file `.env.example` (nếu có) và điền thông tin của mình.

### Cách 2: Sử dụng Docker

1. Tạo file `.env` với các biến môi trường (xem phần trên)

2. Build Docker image:
```bash
sudo docker-compose build
```

3. Chạy container:
```bash
sudo docker-compose up -d
```

4. Xem logs:
```bash
sudo docker-compose logs -f telegram-bot
```

5. Dừng container:
```bash
sudo docker-compose down
```

> ⚠️ **Lưu ý**: 
> - Trên Linux, có thể cần dùng `sudo` hoặc thêm user vào docker group
> - Dữ liệu được lưu trong Docker volumes, sẽ không mất khi xóa container

## 🚀 Sử dụng

### Các lệnh chính

- `/start` - Bắt đầu sử dụng bot và hiển thị menu chính
- `/inbill` - Ghi lại hóa đơn mới (tên khách, SĐT, dịch vụ, số tiền)
- `/expense` - Ghi lại khoản chi tiêu (loại chi phí, số tiền, ghi chú)
- `/report` - Tạo báo cáo doanh thu và chi phí
- `/cancel` - Hủy thao tác hiện tại

### Quy trình sử dụng

1. **Nhập hóa đơn** (`/inbill`):
   - Nhập tên khách hàng
   - Nhập số điện thoại (10 số, bắt đầu bằng 0)
   - Nhập tên dịch vụ
   - Nhập số tiền (VNĐ)
   - Nhập ghi chú (tùy chọn)
   - Xác nhận → Bot sẽ tạo QR code thanh toán (nếu đã cấu hình BANK_ACCOUNT)

2. **Nhập chi phí** (`/expense`):
   - Nhập loại chi phí (ví dụ: Mua nguyên liệu, Điện nước, Lương...)
   - Nhập số tiền
   - Nhập ghi chú (tùy chọn)
   - Xác nhận

3. **Xem báo cáo** (`/report`):
   - Chọn tháng hiện tại
   - Chọn tháng trước
   - Hoặc nhập khoảng thời gian tùy chỉnh (format: `yyyy-mm-dd to yyyy-mm-dd`)
   - Bot sẽ gửi báo cáo text và file CSV chi tiết
## 📁 Cấu trúc Project

```
telegram-chat-bot/
├── bot.py              # File chính để khởi động bot
├── handlers.py         # Xử lý các lệnh và conversation handlers
├── db.py               # Quản lý cơ sở dữ liệu SQLite
├── utils.py            # Các hàm tiện ích (QR code generation)
├── config.py           # Module quản lý cấu hình tập trung
├── requirements.txt    # Danh sách các dependency Python
├── docker-compose.yml  # Cấu hình Docker Compose
├── Dockerfile          # Cấu hình Docker image
├── entrypoint.sh       # Script khởi động cho Docker container
├── .dockerignore       # Files bỏ qua khi build Docker image
├── .env                # File cấu hình môi trường (không commit)
└── README.md           # Tài liệu hướng dẫn
```

## 📦 Dependencies chính

### Core Dependencies (Bắt buộc)
- `python-telegram-bot==20.3` - Thư viện Telegram Bot API
- `python-dotenv>=1.0.0` - Quản lý biến môi trường từ file .env

### Optional Dependencies (Đã comment trong requirements.txt)
Các thư viện sau có thể được uncomment nếu cần:
- `pandas` - Xử lý dữ liệu (hiện chưa sử dụng)
- `pillow` - Xử lý hình ảnh (hiện chưa sử dụng)
- `numpy` - Tính toán số học (hiện chưa sử dụng)
- `qrcode` - Tạo QR code (hiện dùng VietQR API thay vì generate local)

> 💡 **Lưu ý**: Bot hiện tại sử dụng VietQR API để tạo QR code, không cần cài thêm thư viện.

## 🛠️ Phát triển

### Kiến trúc

1. **Bot Framework**: Sử dụng `python-telegram-bot` v20.3 với async/await
2. **Database**: SQLite với context manager để quản lý connections an toàn
3. **Configuration**: Module `config.py` quản lý tất cả cấu hình tập trung
4. **Error Handling**: Logging chi tiết với stack traces
5. **Type Hints**: Code có đầy đủ type hints để dễ maintain

### Cấu trúc Database

**Bảng `sales`** (Doanh thu):
- `id`, `name`, `phone`, `service`, `amount`, `note`, `created_at`, `updated_at`

**Bảng `expenses`** (Chi phí):
- `id`, `category`, `amount`, `note`, `created_at`, `updated_at`

### Chạy local development

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# hoặc
.\venv\Scripts\activate  # Windows

# Chạy bot
python bot.py
```

### Testing Database

```bash
python db.py
```

Sẽ hiển thị thống kê database hiện tại.

## 🐛 Troubleshooting

### Lỗi thường gặp

**1. ModuleNotFoundError: No module named 'telegram'**
- Đảm bảo đã cài đặt dependencies: `pip install -r requirements.txt`
- Nếu dùng Docker, rebuild image: `sudo docker-compose build --no-cache`

**2. Permission denied khi chạy Docker**
- Thêm user vào docker group: `sudo usermod -aG docker $USER` (cần logout/login lại)
- Hoặc dùng `sudo` trước các lệnh docker

**3. Bot không kết nối được**
- Kiểm tra `BOT_TOKEN` trong file `.env`
- Đảm bảo token hợp lệ từ [@BotFather](https://t.me/botfather)

**4. QR code không được tạo**
- Kiểm tra `BANK_ACCOUNT` và `BANK_CODE` trong file `.env`
- Bot vẫn hoạt động bình thường, chỉ không tạo QR code

**5. Database permission error**
- Kiểm tra quyền ghi vào thư mục chứa database
- Với Docker, entrypoint sẽ tự động fix permissions

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

### Code Style

- Sử dụng type hints cho tất cả functions
- Follow PEP 8 style guide
- Thêm docstrings cho các functions/classes
- Test code trước khi commit

## 📄 License

[MIT License](LICENSE)

## 👤 Tác giả

- **vindevops99** - *Initial work* - [GitHub](https://github.com/vindevops99)

Project được khởi tạo bởi [vindevops99](https://github.com/vindevops99/list-opensource)

## 🙏 Cảm ơn

Cảm ơn bạn đã sử dụng bot này! Nếu có bất kỳ câu hỏi hoặc đề xuất nào, vui lòng tạo issue trên GitHub.

---

⭐ **Nếu project này hữu ích, hãy star repository để ủng hộ!** ⭐