# handlers.py - Fixed & Improved Version
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters
)
from db import get_db
from utils import generate_qr
from config import Config
import csv
import os
import logging
import re
from datetime import datetime
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)


def get_vn_time() -> str:
    """Lấy thời gian hiện tại theo múi giờ Việt Nam"""
    vn_timezone = Config.get_timezone_info()
    return datetime.now(vn_timezone).strftime("%Y-%m-%d %H:%M:%S")

# ===========================
# States
# ===========================
# /inbill
NAME, PHONE, SERVICE, AMOUNT, NOTE, CONFIRM = range(6)
# /report
REPORT_CHOICE, REPORT_CUSTOM = range(2)
# /expense
EXP_CATEGORY, EXP_AMOUNT, EXP_NOTE, EXP_CONFIRM = range(4)

# ===========================
# /start
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler cho lệnh /start"""
    if update.message:
        await update.message.reply_text("👋 Xin chào! Chào mừng bạn đến với hệ thống quản lý.")
        await send_main_menu(update, context)

# ===========================
# Echo text
# ===========================
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo lại text từ user"""
    if update.message and update.message.text:
        await update.message.reply_text(
            f"💬 Bạn vừa gửi: {update.message.text}\n\n"
            "Vui lòng chọn chức năng từ menu hoặc dùng lệnh:\n"
            "/inbill - Thu tiền\n"
            "/expense - Chi phí\n"
            "/report - Báo cáo\n"
            "/cancel - Để hủy thao tác hiện tại."
        )
        await send_main_menu(update, context)

# ====================
# Gửi menu thao tác
# ====================
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi menu chính với 3 lựa chọn"""
    keyboard = [
        [
            InlineKeyboardButton("💵 Thu tiền", callback_data="goto_inbill"),
            InlineKeyboardButton("💸 Chi phí", callback_data="goto_expense"),
        ],
        [
            InlineKeyboardButton("📊 Báo cáo", callback_data="goto_report"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    menu_text = "➡️ Tôi là Nô Tỳ của HongDaoBrown, mời bạn chọn thao tác:"

    # Gửi menu
    if update.callback_query:
        await update.callback_query.message.reply_text(menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

async def menu_callback_inbill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback để vào flow inbill từ menu"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("💵 *NHẬP HÓA ĐƠN*\n\nNhập tên khách hàng:", parse_mode="Markdown")
    return NAME

async def menu_callback_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback để vào flow expense từ menu"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "💸 *NHẬP CHI PHÍ*\n\nNhập loại chi phí:\nVí dụ: Mua nguyên liệu, Điện nước, Lương...",
        parse_mode="Markdown"
    )
    return EXP_CATEGORY

async def menu_callback_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback để vào flow report từ menu"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📅 Tháng hiện tại", callback_data="month_current")],
        [InlineKeyboardButton("📆 Tháng trước", callback_data="month_previous")],
        [InlineKeyboardButton("📌 Tùy chỉnh ngày", callback_data="custom_date")]
    ]
    await query.message.reply_text(
        "📊 *BÁO CÁO*\n\nChọn loại báo cáo:", 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return REPORT_CHOICE

# ===========================
# /inbill ConversationHandler
# ===========================
async def start_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu flow nhập hóa đơn"""
    await update.message.reply_text("💵 *NHẬP HÓA ĐƠN*\n\nNhập tên khách hàng:", parse_mode="Markdown")
    return NAME

async def name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập tên khách hàng"""
    name = update.message.text.strip()
    
    if len(name) < 2:
        await update.message.reply_text("❌ Tên quá ngắn. Vui lòng nhập lại:")
        return NAME
    
    context.user_data["name"] = name
    await update.message.reply_text("📞 Nhập số điện thoại (10 chữ số, bắt đầu bằng 0):")
    return PHONE

async def phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập và validate số điện thoại"""
    phone = update.message.text.strip()
    
    # Validate SĐT Việt Nam: 10 số, bắt đầu bằng 0
    if not re.match(r'^0\d{9}$', phone):
        await update.message.reply_text(
            "❌ Số điện thoại không hợp lệ!\n"
            "Vui lòng nhập 10 chữ số, bắt đầu bằng 0.\n"
            "Ví dụ: 0901234567"
        )
        return PHONE
    
    context.user_data["phone"] = phone
    await update.message.reply_text("💇 Nhập tên dịch vụ:")
    return SERVICE

async def service_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập tên dịch vụ"""
    service = update.message.text.strip()
    
    if len(service) < 2:
        await update.message.reply_text("❌ Tên dịch vụ quá ngắn. Vui lòng nhập lại:")
        return SERVICE
    
    context.user_data["service"] = service
    await update.message.reply_text("💰 Nhập số tiền (VNĐ):")
    return AMOUNT

async def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập và validate số tiền"""
    try:
        # Loại bỏ dấu phẩy, dấu chấm nếu có
        amount_str = update.message.text.strip().replace(",", "").replace(".", "")
        amount = int(amount_str)
        
        if amount <= 0:
            await update.message.reply_text("❌ Số tiền phải lớn hơn 0. Vui lòng nhập lại:")
            return AMOUNT
        
        if amount > 1000000000:  # 1 tỷ
            await update.message.reply_text("❌ Số tiền quá lớn. Vui lòng kiểm tra lại:")
            return AMOUNT
        
        context.user_data["amount"] = amount
        await update.message.reply_text("📝 Ghi chú khác (nếu có, hoặc nhập '-' để bỏ qua):")
        return NOTE
        
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số tiền hợp lệ (chỉ chứa số):")
        return AMOUNT

async def note_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập ghi chú và hiển thị xác nhận"""
    note_text = update.message.text.strip()
    note = "" if note_text.lower() in ["bỏ qua", "-", "skip"] else note_text
    context.user_data["note"] = note
    
    data = context.user_data

    text = (
        f"📋 *XÁC NHẬN HÓA ĐƠN*\n\n"
        f"👤 Tên: `{data['name']}`\n"
        f"📞 SĐT: `{data['phone']}`\n"
        f"💇 Dịch vụ: `{data['service']}`\n"
        f"💰 Số tiền: `{data['amount']:,}đ`\n"
        f"📝 Ghi chú: `{data['note'] or '(Không có)'}`"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Xác nhận", callback_data="confirm_bill_ok"),
            InlineKeyboardButton("❌ Hủy", callback_data="confirm_bill_cancel")
        ]
    ]
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CONFIRM

async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý xác nhận hóa đơn"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_bill_ok":
        data = context.user_data
        
        try:
            # Lưu vào database
            with get_db() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO sales (name, phone, service, amount, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (data["name"], data["phone"], data["service"], data["amount"], data["note"], get_vn_time())
                )
            
            logger.info(f"Saved bill for {data['name']} - {data['service']} - {data['amount']:,}đ")
            
            # Tạo QR thanh toán
            try:
                qr_link = generate_qr(data["amount"], data["phone"], data["service"])
                
                # Gửi thông báo thành công
                await query.edit_message_text(
                    f"✅ *ĐÃ LƯU HÓA ĐƠN THÀNH CÔNG!*\n\n"
                    f"👤 Khách hàng: `{data['name']}`\n"
                    f"💇 Dịch vụ: `{data['service']}`\n"
                    f"💰 Số tiền: `{data['amount']:,}đ`\n"
                    f"📝 Ghi chú: `{data['note'] or '(Không có)'}`\n\n"
                    f"📱 QR thanh toán đang được gửi...",
                    parse_mode="Markdown"
                )
                
                # Gửi QR code
                await query.message.reply_photo(
                    qr_link,
                    caption=f"💳 Quét mã QR để thanh toán {data['amount']:,}đ"
                )
                
            except ValueError as e:
                # BANK_ACCOUNT chưa được cấu hình
                logger.warning(f"QR code generation skipped: {e}")
                await query.edit_message_text(
                    f"✅ *ĐÃ LƯU HÓA ĐƠN THÀNH CÔNG!*\n\n"
                    f"👤 Khách hàng: `{data['name']}`\n"
                    f"💇 Dịch vụ: `{data['service']}`\n"
                    f"💰 Số tiền: `{data['amount']:,}đ`\n"
                    f"📝 Ghi chú: `{data['note'] or '(Không có)'}`\n\n"
                    f"⚠️ *Lưu ý*: Mã QR chưa được tạo. Vui lòng cấu hình BANK_ACCOUNT trong file .env",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Error generating/sending QR: {e}", exc_info=True)
                await query.message.reply_text(
                    f"⚠️ Không thể tạo mã QR.\n"
                    f"Vui lòng thu tiền thủ công.\n\n"
                    f"Lỗi: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Database error when saving bill: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ *LỖI LƯU DỮ LIỆU!*\n\n"
                "Vui lòng thử lại sau.\n\n"
                f"Chi tiết lỗi: {str(e)}",
                parse_mode="Markdown"
            )
            context.user_data.clear()
            return ConversationHandler.END
    
    else:  # confirm_bill_cancel
        await query.edit_message_text("❌ Đã hủy nhập hóa đơn.")
        logger.info("Bill cancelled by user")

    context.user_data.clear()
    
    # Gửi menu sau khi hoàn tất
    await send_main_menu(update, context)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Hủy flow hiện tại"""
    if update.message:
        await update.message.reply_text("❌ Đã hủy thao tác.")
    context.user_data.clear()
    await send_main_menu(update, context)
    return ConversationHandler.END

def get_inbill_handler():
    """Tạo ConversationHandler cho /inbill"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("inbill", start_bill),
            CallbackQueryHandler(menu_callback_inbill, pattern="^goto_inbill$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_input)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_input)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, service_input)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, note_input)],
            CONFIRM: [CallbackQueryHandler(confirm_callback, pattern="^confirm_bill_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

# ===========================
# /expense ConversationHandler
# ===========================
async def start_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu flow nhập chi phí"""
    await update.message.reply_text(
        "💸 *NHẬP CHI PHÍ*\n\n"
        "Nhập loại chi phí:\n"
        "Ví dụ: Mua nguyên liệu, Điện nước, Lương...",
        parse_mode="Markdown"
    )
    return EXP_CATEGORY

async def expense_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập loại chi phí"""
    category = update.message.text.strip()
    
    if len(category) < 2:
        await update.message.reply_text("❌ Loại chi phí quá ngắn. Vui lòng nhập lại:")
        return EXP_CATEGORY
    
    context.user_data["category"] = category
    await update.message.reply_text("💰 Nhập số tiền chi:")
    return EXP_AMOUNT

async def expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập và validate số tiền chi"""
    try:
        amount_str = update.message.text.strip().replace(",", "").replace(".", "")
        amount = float(amount_str)
        
        if amount <= 0:
            await update.message.reply_text("❌ Số tiền phải lớn hơn 0. Vui lòng nhập lại:")
            return EXP_AMOUNT
        
        if amount > 1000000000:
            await update.message.reply_text("❌ Số tiền quá lớn. Vui lòng kiểm tra lại:")
            return EXP_AMOUNT
        
        context.user_data["amount"] = amount
        await update.message.reply_text("📝 Ghi chú (nếu có, hoặc nhập '-' để bỏ qua):")
        return EXP_NOTE
        
    except ValueError:
        await update.message.reply_text("❌ Vui lòng nhập số tiền hợp lệ (chỉ chứa số):")
        return EXP_AMOUNT

async def expense_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhập ghi chú chi phí và hiển thị xác nhận"""
    note_text = update.message.text.strip()
    note = "" if note_text in ["-", "skip"] else note_text
    context.user_data["note"] = note

    category = context.user_data["category"]
    amount = context.user_data["amount"]

    keyboard = [
        [
            InlineKeyboardButton("✅ Xác nhận", callback_data="confirm_exp_ok"),
            InlineKeyboardButton("❌ Hủy", callback_data="confirm_exp_cancel"),
        ]
    ]
    
    await update.message.reply_text(
        f"🔍 *XÁC NHẬN CHI PHÍ*\n\n"
        f"• Loại: `{category}`\n"
        f"• Số tiền: `{amount:,.0f}đ`\n"
        f"• Ghi chú: `{note or '(Không có)'}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    return EXP_CONFIRM

async def confirm_expense_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý xác nhận chi phí"""
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_exp_ok":
        category = context.user_data["category"]
        amount = context.user_data["amount"]
        note = context.user_data["note"]

        try:
            # Lưu vào database
            with get_db() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO expenses (category, amount, note, created_at) VALUES (?, ?, ?, ?)",
                    (category, amount, note, get_vn_time()),
                )
            
            logger.info(f"Saved expense: {category} - {amount:,.0f}đ")
            
            await query.edit_message_text(
                f"✅ *ĐÃ LƯU CHI PHÍ THÀNH CÔNG!*\n\n"
                f"• Loại: `{category}`\n"
                f"• Số tiền: `{amount:,.0f}đ`\n"
                f"• Ghi chú: `{note or '(Không có)'}`",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Database error when saving expense: {e}", exc_info=True)
            await query.edit_message_text(
                "❌ *LỖI LƯU DỮ LIỆU!*\n\n"
                "Vui lòng thử lại sau.\n\n"
                f"Chi tiết lỗi: {str(e)}",
                parse_mode="Markdown"
            )

    else:  # confirm_exp_cancel
        await query.edit_message_text("❌ Đã hủy nhập chi phí.")
        logger.info("Expense cancelled by user")

    context.user_data.clear()
    
    # Gửi menu sau khi hoàn tất
    await send_main_menu(update, context)
    
    return ConversationHandler.END

def get_expense_handler():
    """Tạo ConversationHandler cho /expense"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("expense", start_expense),
            CallbackQueryHandler(menu_callback_expense, pattern="^goto_expense$")
        ],
        states={
            EXP_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_category)],
            EXP_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_amount)],
            EXP_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_note)],
            EXP_CONFIRM: [CallbackQueryHandler(confirm_expense_callback, pattern="^confirm_exp_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

# ===========================
# /report ConversationHandler
# ===========================
async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu flow báo cáo"""
    keyboard = [
        [InlineKeyboardButton("📅 Tháng hiện tại", callback_data="month_current")],
        [InlineKeyboardButton("📆 Tháng trước", callback_data="month_previous")],
        [InlineKeyboardButton("📌 Tùy chỉnh ngày", callback_data="custom_date")]
    ]
    await update.message.reply_text(
        "📊 *BÁO CÁO*\n\nChọn loại báo cáo:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return REPORT_CHOICE

async def report_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lựa chọn loại báo cáo"""
    query = update.callback_query
    await query.answer()

    if query.data == "month_current":
        await query.edit_message_text("⏳ Đang tạo báo cáo tháng hiện tại...")
        await generate_report(update, context, report_type="current", message=query.message)
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    elif query.data == "month_previous":
        await query.edit_message_text("⏳ Đang tạo báo cáo tháng trước...")
        await generate_report(update, context, report_type="previous", message=query.message)
        await send_main_menu(update, context)
        return ConversationHandler.END
        
    elif query.data == "custom_date":
        await query.edit_message_text(
            "📅 *NHẬP KHOẢNG THỜI GIAN*\n\n"
            "Format: `yyyy-mm-dd to yyyy-mm-dd`\n"
            "Ví dụ: `2025-11-01 to 2025-11-03`",
            parse_mode="Markdown"
        )
        return REPORT_CUSTOM

async def report_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý nhập ngày tùy chỉnh"""
    text = update.message.text.strip()
    
    try:
        # Parse input
        parts = [s.strip() for s in text.lower().split("to")]
        if len(parts) != 2:
            raise ValueError("Invalid format")
        
        start_str, end_str = parts
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        
        # Validate dates
        if start_date > end_date:
            await update.message.reply_text(
                "❌ Ngày bắt đầu phải trước ngày kết thúc.\n"
                "Vui lòng nhập lại."
            )
            return REPORT_CUSTOM
        
        if (end_date - start_date).days > 365:
            await update.message.reply_text(
                "❌ Khoảng thời gian quá dài (tối đa 365 ngày).\n"
                "Vui lòng nhập lại."
            )
            return REPORT_CUSTOM
        
        await update.message.reply_text("⏳ Đang tạo báo cáo...")
        await generate_report(update, context, start_date, end_date, message=update.message)
        
    except ValueError:
        await update.message.reply_text(
            "❌ *FORMAT KHÔNG HỢP LỆ!*\n\n"
            "Vui lòng nhập đúng format:\n"
            "`yyyy-mm-dd to yyyy-mm-dd`\n\n"
            "Ví dụ: `2025-11-01 to 2025-11-03`",
            parse_mode="Markdown"
        )
        return REPORT_CUSTOM

    await send_main_menu(update, context)
    return ConversationHandler.END

async def generate_report(update, context, start_date=None, end_date=None, report_type=None, message=None):
    """Tạo báo cáo doanh thu và chi phí"""
    if message is None:
        message = update.message

    try:
        with get_db() as conn:
            c = conn.cursor()
            
            # Xác định khoảng thời gian
            vn_timezone = Config.get_timezone_info()
            
            if report_type == "current":
                now = datetime.now(vn_timezone)
                year, month = now.year, now.month
                where_clause = "strftime('%Y', created_at)=? AND strftime('%m', created_at)=?"
                params = (str(year), f"{month:02d}")
                period_text = f"tháng {month}/{year}"
                
            elif report_type == "previous":
                now = datetime.now(vn_timezone)
                if now.month == 1:
                    year, month = now.year - 1, 12
                else:
                    year, month = now.year, now.month - 1
                where_clause = "strftime('%Y', created_at)=? AND strftime('%m', created_at)=?"
                params = (str(year), f"{month:02d}")
                period_text = f"tháng {month}/{year}"
                
            else:  # Custom date range
                where_clause = "date(created_at) BETWEEN ? AND ?"
                params = (str(start_date), str(end_date))
                period_text = f"{start_date} đến {end_date}"
            
            # Lấy dữ liệu sales
            c.execute(f"""
                SELECT id, name, phone, service, amount, note, created_at
                FROM sales
                WHERE {where_clause}
                ORDER BY created_at DESC
            """, params)
            sales_rows = c.fetchall()
            
            # Lấy dữ liệu expenses
            c.execute(f"""
                SELECT id, category, amount, note, created_at
                FROM expenses
                WHERE {where_clause}
                ORDER BY created_at DESC
            """, params)
            expense_rows = c.fetchall()

        # Tính toán
        total_sales = sum(row[4] for row in sales_rows)
        total_expenses = sum(row[2] for row in expense_rows)
        profit = total_sales - total_expenses
        
        # Tạo text báo cáo
        profit_emoji = "📈" if profit >= 0 else "📉"
        profit_text = f"+{profit:,}" if profit >= 0 else f"{profit:,}"
        
        text_report = (
            f"📊 *BÁO CÁO TỔNG HỢP*\n"
            f"Kỳ: _{period_text}_\n\n"
            f"💵 *Doanh thu*\n"
            f"• Số hóa đơn: `{len(sales_rows)}`\n"
            f"• Tổng thu: `{total_sales:,}đ`\n\n"
            f"💸 *Chi phí*\n"
            f"• Số khoản chi: `{len(expense_rows)}`\n"
            f"• Tổng chi: `{total_expenses:,}đ`\n\n"
            f"{profit_emoji} *Lãi/Lỗ*: `{profit_text}đ`"
        )
        
        await message.reply_text(text_report, parse_mode="Markdown")
        
        # Tạo CSV nếu có dữ liệu
        if sales_rows or expense_rows:
            os.makedirs("report", exist_ok=True)
            vn_timezone = Config.get_timezone_info()
            csv_filename = f"report/report_{datetime.now(vn_timezone).strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                
                # Sheet 1: Sales
                writer.writerow(["=== DOANH THU ==="])
                writer.writerow(["ID", "Tên khách hàng", "SĐT", "Dịch vụ", "Số tiền", "Ghi chú", "Ngày tạo"])
                for row in sales_rows:
                    writer.writerow(row)
                
                writer.writerow([])
                
                # Sheet 2: Expenses
                writer.writerow(["=== CHI PHÍ ==="])
                writer.writerow(["ID", "Loại chi phí", "Số tiền", "Ghi chú", "Ngày tạo"])
                for row in expense_rows:
                    writer.writerow(row)
                
                writer.writerow([])
                writer.writerow(["=== TỔNG KẾT ==="])
                writer.writerow(["Tổng doanh thu", f"{total_sales:,}đ"])
                writer.writerow(["Tổng chi phí", f"{total_expenses:,}đ"])
                writer.writerow(["Lãi/Lỗ", f"{profit_text}đ"])

            with open(csv_filename, "rb") as f:
                await message.reply_document(f, caption="📄 File báo cáo chi tiết")
                
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        await message.reply_text(
            f"❌ Có lỗi xảy ra khi tạo báo cáo.\n\n"
            f"Chi tiết lỗi: {str(e)}\n\n"
            f"Vui lòng thử lại sau."
        )

def get_report_handler():
    """Tạo ConversationHandler cho /report"""
    return ConversationHandler(
        entry_points=[
            CommandHandler("report", start_report),
            CallbackQueryHandler(menu_callback_report, pattern="^goto_report$")
        ],
        states={
            REPORT_CHOICE: [CallbackQueryHandler(report_choice_callback)],
            REPORT_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_custom_date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
