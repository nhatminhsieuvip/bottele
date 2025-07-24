from telegram import Update, InputFile, User
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
import io

TOKEN = '7550142487:AAHIm7uxWug1vlJId18ospVz1fZpoYLaRgA'  # <-- Đặt token của bạn vào đây

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    target_user: User = None

    # Trường hợp trả lời tin nhắn ai đó
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user

    # Trường hợp nhập username hoặc ID trong lệnh
    elif args:
        query = args[0]
        try:
            if query.startswith("@"):
                query = query[1:]

            target_chat = await context.bot.get_chat(query)
            target_user = target_chat
        except Exception as e:
            await update.message.reply_text("❌ Không tìm thấy người dùng hoặc chưa gặp")
            return

    # Nếu không có gì thì lấy người gửi
    else:
        target_user = update.effective_user

    # Lấy thông tin người dùng
    full_name = target_user.full_name
    mention = target_user.mention_html()
    username = f"@{target_user.username}" if target_user.username else "Không có"
    user_id = target_user.id

    # Lấy bio
    chat_info = await context.bot.get_chat(user_id)
    bio = chat_info.bio or "Không có"

    # Lấy avatar
    photos = await context.bot.get_user_profile_photos(user_id, limit=1)
    photo_count = photos.total_count
    if photo_count > 0:
        file = await context.bot.get_file(photos.photos[0][-1].file_id)
        avatar_data = await file.download_as_bytearray()
        avatar = Image.open(io.BytesIO(avatar_data)).resize((300,300)).convert("RGBA")
    else:
        avatar = Image.new("RGBA", (300,300), (200, 200, 200, 255))  # Nền trống

    # Làm avatar tròn
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 300,300), fill=255)
    avatar.putalpha(mask)

    # Nền template
    base = Image.open("template.jpg").convert("RGBA")
    base.paste(avatar, (65,60), avatar)

    # Xuất ảnh
    output = io.BytesIO()
    base.save(output, format="PNG")
    output.seek(0)

    # Caption
    caption = f"""
<b>👤 Thông Tin Người Dùng</b>

🪪 Tên: {mention}
🔤 Username: {username}
🆔 ID: <code>{user_id}</code>
📄 Bio:
<blockquote>{bio}</blockquote>
🖼 Avatar hiện có: <b>{photo_count}</b>
""".strip()

    await update.message.reply_photo(
        photo=InputFile(output, filename="info.png"),
        caption=caption,
        parse_mode="HTML"
    )


# Khởi động bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("thongtin", info))
app.run_polling()