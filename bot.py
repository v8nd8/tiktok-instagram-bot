import logging
from telegram import Update, InputMediaVideo
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import instaloader
import re
from io import BytesIO

# Конфигурация
BOT_TOKEN = "7240087170:AAEYeJrZyYPleAX0pwTRPwmW3dwKbe5GIog"
CHANNEL_ID = "@mirznan1"
ADMIN_ID = 5257370393

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверка подписки
def check_subscription(user_id: int, context: CallbackContext) -> bool:
    try:
        member = context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Subscription check failed: {e}")
        return False

# Скачивание TikTok (заглушка - нужно API)
def download_tiktok(url: str):
    try:
        # Здесь должен быть код для TikTok API
        return "video.mp4"
    except Exception as e:
        logger.error(f"TikTok download error: {e}")
        return None

# Скачивание Instagram
def download_instagram(url: str):
    try:
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        return post.video_url if post.is_video else None
    except Exception as e:
        logger.error(f"Instagram download error: {e}")
        return None

# Обработчик команд
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    if check_subscription(user.id, context):
        update.message.reply_text(
            f"Привет, {user.first_name}! Отправь мне ссылку на видео из:\n"
            "• TikTok\n• Instagram\n\n"
            "Я скачаю и пришлю его тебе!"
        )
    else:
        update.message.reply_text(
            f"❌ Для использования бота подпишитесь на канал {CHANNEL_ID}\n"
            "После подписки нажмите /start снова"
        )

def handle_message(update: Update, context: CallbackContext):
    if not check_subscription(update.effective_user.id, context):
        update.message.reply_text(f"❌ Подпишитесь на {CHANNEL_ID} для доступа!")
        return

    url = update.message.text
    if not url:
        return

    update.message.reply_text("⏳ Обрабатываю ссылку...")

    try:
        if "tiktok.com" in url:
            video_path = download_tiktok(url)
            if video_path:
                with open(video_path, 'rb') as video_file:
                    update.message.reply_video(video=video_file)
            else:
                update.message.reply_text("⚠ Не удалось скачать видео с TikTok")
        
        elif "instagram.com" in url:
            video_url = download_instagram(url)
            if video_url:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    video_bytes = BytesIO(response.content)
                    video_bytes.seek(0)
                    update.message.reply_video(video=video_bytes)
                else:
                    update.message.reply_text("⚠ Ошибка загрузки видео")
            else:
                update.message.reply_text("ℹ Это не видео или ссылка неверна")
        
        else:
            update.message.reply_text("❌ Отправьте ссылку на TikTok или Instagram")

    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("⚠ Произошла ошибка. Попробуйте другую ссылку")

def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")
    if update.effective_message:
        update.effective_message.reply_text("⚠ Произошла ошибка. Попробуйте позже")

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("Бот запущен и работает...")
    updater.idle()

if __name__ == "__main__":
    main()
