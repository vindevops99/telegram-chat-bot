#!/bin/bash
set -e

APP_DIR="/app"
ENV_FILE="$APP_DIR/.env"
EXAMPLE_ENV="$APP_DIR/.env.example"
SQL_DIR="$APP_DIR/sqlite3"
REPORT_DIR="$APP_DIR/report"
LOG_FILE="$APP_DIR/bot.log"

# If .env doesn't exist, copy from example (safe convenience for dev)
if [ ! -f "$ENV_FILE" ] && [ -f "$EXAMPLE_ENV" ]; then
  echo "[entrypoint] .env not found, copying from .env.example"
  cp "$EXAMPLE_ENV" "$ENV_FILE"
  chmod 600 "$ENV_FILE" || true
fi

# Ensure sqlite3 folder and report directory exist and are writable
mkdir -p "$SQL_DIR"
mkdir -p "$REPORT_DIR"
chmod -R 777 "$REPORT_DIR" "$SQL_DIR"
chmod 666 "$LOG_FILE"
# ensure log file exists
touch "$LOG_FILE"

# Fix ownership if running as root and botuser exists
if id "botuser" &>/dev/null; then
  chown -R botuser:botuser "$APP_DIR" || true
fi

# If BOT_TOKEN is empty, warn (we don't exit because user may still want the container up)
if [ -z "${BOT_TOKEN:-}" ]; then
  echo "[entrypoint] WARNING: BOT_TOKEN is not set. Bot will not be able to connect without a token."
fi

# Exec the main process (the CMD in Dockerfile will be used as arguments)
# Drop privileges to botuser using gosu if available
if command -v gosu >/dev/null 2>&1; then
  echo "[entrypoint] Dropping privileges to 'botuser' and execing: $@"
  exec gosu botuser "$@"
else
  echo "[entrypoint] gosu not found, running as current user: $@"
  exec "$@"
fi
