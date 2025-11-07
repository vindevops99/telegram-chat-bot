# ===============================
# Stage 1: Build dependencies
# ===============================
FROM python:3.10-slim AS builder

WORKDIR /app

# Cài đặt build dependencies nếu cần
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ===============================
# Stage 2: Runtime
# ===============================
FROM python:3.10-slim

# Metadata
LABEL maintainer="vindevops99"
LABEL description="Telegram Chat Bot for Sales and Expense Management"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Tạo thư mục làm việc
WORKDIR /app

# Copy Python packages từ builder stage (system-wide installation)
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy mã nguồn và script entrypoint
COPY --chown=root:root entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy mã nguồn (sẽ được chown trong entrypoint)
COPY . /app

# Tạo user không phải root để chạy an toàn
RUN adduser --disabled-password --gecos "" botuser && \
    mkdir -p /app/sqlite3 /app/report && \
    chown -R botuser:botuser /app/sqlite3 /app/report

# Healthcheck để monitor bot status
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Đặt user mặc định (entrypoint sẽ chuyển sang botuser)
USER root

# Entrypoint để tự fix quyền, tạo file .env và log khi start
ENTRYPOINT ["/app/entrypoint.sh"]

# Lệnh mặc định chạy bot
CMD ["python", "bot.py"]