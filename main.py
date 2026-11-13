from flask import Flask
import threading
import os
import logging
import os
import shutil
import uuid
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# ===================== CẤU HÌNH =====================
# Cho phép nhiều group ID dùng bot
ALLOWED_CHAT_IDS = [-5463365004, -5463365004]

# ===================== XỬ LÝ ẢNH MB =====================

def format_money(value):
    if value == int(value):
        return f"{int(value):,} VND"
    else:
        return f"{value:,.2f} VND"

def draw_centered_text(draw, image_width, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)

def create_image_with_texts(
    sotienchuyen,
    thoigianchuyen,
    tennguoinhan,
    stk,
    noidungchuyen,
    y_money=670,
    y_time=810,
    y_name=1050,
    y_stk=1250,
    y_noidung=1310
):
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    # luôn xóa file cũ trong thư mục out
    for f in os.listdir(output_dir):
        try:
            os.remove(os.path.join(output_dir, f))
        except:
            pass

    image = Image.open("mb.png")
    draw = ImageDraw.Draw(image)
    image_width, _ = image.size

    # Font
    font_path = "font/sotien.otf"
    averta_font_path = "font/sotien.otf"

    font_money = ImageFont.truetype(font_path, 97)
    font_time = ImageFont.truetype(font_path, 44)
    font_name = ImageFont.truetype(font_path, 70)
    font_stk = ImageFont.truetype(averta_font_path, 40)
    font_ndck = ImageFont.truetype(averta_font_path, 40)

    # Màu chữ
    color_money = (33, 33, 200)
    color_time = (128, 128, 128)
    color_name = (37, 45, 66)
    color_content = (37, 45, 66)

    # Vẽ text
    draw_centered_text(draw, image_width, y_money, format_money(sotienchuyen), font_money, color_money)
    draw_centered_text(draw, image_width, y_time, thoigianchuyen, font_time, color_time)
    draw_centered_text(draw, image_width, y_name, tennguoinhan, font_name, color_name)
    draw_centered_text(draw, image_width, y_stk, stk, font_stk, color_content)
    draw_centered_text(draw, image_width, y_noidung, noidungchuyen, font_ndck, color_content)

    output_path = os.path.join(output_dir, "latest.png")
    image.save(output_path)
    return output_path

# ===================== LỆNH BOT =====================

# Hàm check ID chat
def check_chat(update: Update) -> bool:
    return update.effective_chat.id in ALLOWED_CHAT_IDS  # ✅ fix ở đây

# /mb
async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_chat(update):
        return  # bỏ qua nếu không phải group cho phép

    full_text = " ".join(context.args)
    parts = full_text.split("|")

    if len(parts) != 5:
        await update.message.reply_text(
            "❌ Sai cú pháp.\n"
            "✅ Đúng: /mb <số tiền> | <giờ:phút> | <tên người nhận> | <STK> | <nội dung chuyển khoản>"
        )
        return

    try:
        sotienchuyen = float(parts[0].strip().replace(',', ''))
        gio_phut = parts[1].strip()
        tennguoinhan = parts[2].strip()
        stk = parts[3].strip()
        noidungchuyen = parts[4].strip()
    except Exception as e:
        await update.message.reply_text(f"Lỗi xử lý tham số: {e}")
        return

    ngay_hom_nay = datetime.now().strftime("%d/%m/%Y")
    thoigianchuyen = f"{gio_phut} - {ngay_hom_nay}"

    try:
        image_path = create_image_with_texts(
            sotienchuyen,
            thoigianchuyen,
            tennguoinhan,
            stk,
            noidungchuyen
        )
    except Exception as e:
        await update.message.reply_text(f"Lỗi khi tạo ảnh: {e}")
        return

    with open(image_path, "rb") as photo:
        await update.message.reply_photo(photo)

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_chat(update):
        return
    await update.message.reply_text(
        "📖 *Hướng dẫn sử dụng:*\n"
        "- /mb : Tạo ảnh MB\n"
        "- /account : Xem thông tin\n"
        "- /menu : Mở menu",
        parse_mode="Markdown"
    )

# /account
async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_chat(update):
        return
    user = update.message.from_user
    await update.message.reply_text(
        f"👤 Username: `{user.username}`\n🆔 ID: `{user.id}`",
        parse_mode="Markdown"
    )

# /menu
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_chat(update):
        return
    keyboard = [
        [KeyboardButton("/mb 💸 Tạo Bill MB")],
        [KeyboardButton("/help ❓ Hướng dẫn"), KeyboardButton("/account 👤 Tài khoản")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("✨ MENU CHÍNH ✨\nChọn lệnh nhanh:", reply_markup=reply_markup)

# ===================== MAIN =====================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def main():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    TOKEN = "9171506250:AAEVw8p4SXuOhJtWkrNslkuzpq8rErQ23Zc"
    TOKEN = "9171506250:AAEvW8p4SXuOhJlWkrNsIkuzpyq8rtErQ23zc"

    if os.path.exists("out"):
        try:
            shutil.rmtree("out")
        except PermissionError:
            pass

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("mb", mb_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("account", account_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    logging.basicConfig(level=logging.CRITICAL)
    print("Bot MB Fake Bill chạy thành công!")
    application.run_polling()

if __name__ == "__main__":
    main()
