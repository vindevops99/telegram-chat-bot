#!/bin/bash
set -euo pipefail

# ============================================
# Configuration
# ============================================
APP_DIR="/app"
ENV_FILE="$APP_DIR/.env"
EXAMPLE_ENV="$APP_DIR/.env.example"
SQL_DIR="$APP_DIR/sqlite3"
REPORT_DIR="$APP_DIR/report"
LOG_FILE="${LOG_FILE:-$APP_DIR/bot.log}"

# Colors for output (optional)
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# ============================================
# Helper Functions
# ============================================
log_info() {
    echo -e "${GREEN}[entrypoint]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[entrypoint] WARNING:${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[entrypoint] ERROR:${NC} $*" >&2
}

# ============================================
# Main Initialization
# ============================================
log_info "Starting container initialization..."

# 1️⃣ Copy .env nếu chưa có
if [ ! -f "$ENV_FILE" ] && [ -f "$EXAMPLE_ENV" ]; then
  log_warn ".env not found, copying from .env.example"
  cp "$EXAMPLE_ENV" "$ENV_FILE"
  chmod 600 "$ENV_FILE" || true
  log_warn "Please update $ENV_FILE with your actual configuration!"
fi

# 2️⃣ Đảm bảo thư mục & file tồn tại
log_info "Creating necessary directories..."
mkdir -p "$SQL_DIR" "$REPORT_DIR" "$(dirname "$LOG_FILE")"
touch "$LOG_FILE" || true

# 3️⃣ Cấp quyền cho botuser truy cập các volume được mount
log_info "Fixing permissions for volumes and logs..."
# Đảm bảo botuser có quyền ghi vào các thư mục cần thiết
chown -R botuser:botuser "$SQL_DIR" "$REPORT_DIR" "$(dirname "$LOG_FILE")" 2>/dev/null || true
chmod 775 "$SQL_DIR" "$REPORT_DIR" 2>/dev/null || true
chmod 664 "$LOG_FILE" 2>/dev/null || true

# Đảm bảo botuser có quyền đọc mã nguồn
chown -R botuser:botuser "$APP_DIR" 2>/dev/null || true
chmod -R 755 "$APP_DIR" 2>/dev/null || true

# 4️⃣ Validate environment variables
log_info "Validating environment variables..."

MISSING_VARS=0

if [ -z "${BOT_TOKEN:-}" ] || [ "${BOT_TOKEN:-}" = "YOUR_TOKEN_HERE" ]; then
  log_error "BOT_TOKEN is not set or invalid!"
  MISSING_VARS=$((MISSING_VARS + 1))
fi

if [ -z "${DB_NAME:-}" ]; then
  log_warn "DB_NAME is not set, using default: /app/sqlite3/sales.db"
fi

if [ -z "${BANK_ACCOUNT:-}" ]; then
  log_warn "BANK_ACCOUNT is not set - QR code generation will be disabled"
fi

if [ -z "${BANK_CODE:-}" ]; then
  log_warn "BANK_CODE is not set, using default: MB"
fi

if [ $MISSING_VARS -gt 0 ]; then
  log_error "Missing required environment variables. Please check your .env file or docker-compose.yml"
  log_error "Bot may fail to start properly."
fi

# 5️⃣ Validate Python và dependencies
log_info "Validating Python environment..."
if ! command -v python &> /dev/null; then
  log_error "Python is not found in PATH!"
  exit 1
fi

if ! python -c "import telegram" &> /dev/null; then
  log_error "python-telegram-bot is not installed!"
  exit 1
fi

log_info "Python environment OK"

# 6️⃣ Chạy app dưới quyền botuser
log_info "Starting bot as botuser..."

# Prefer runuser or su; fall back to running as current user if neither exists.
if command -v runuser >/dev/null 2>&1; then
  log_info "Using runuser to drop privileges and start bot"
  exec runuser -u botuser -- python bot.py
elif command -v su >/dev/null 2>&1; then
  log_info "Using su to drop privileges and start bot"
  # Use -s to specify shell for su; this helps on some minimal images
  exec su -s /bin/bash botuser -c "python bot.py"
else
  log_warn "neither runuser nor su available, starting as current user (NOT RECOMMENDED)"
  exec python bot.py
fi
