import os
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7240087170:AAEYeJrZyYPleAX0pwTRPwmW3dwKbe5GIog'  # Ваш токен бота
CHANNEL = '@mirznan1'  # Ваш канал (начинается с @)

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n"
        "📤 Отправь мне ссылку из TikTok или Instagram, и я скачаю видео!\n"
        f"📢 Подпишись на канал: {CHANNEL}"
    )

def is_subscribed(user_id: int, context: CallbackContext) -> bool:
    try:
        member = context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False  # Если ошибка, считаем, что не подписан

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if not is_subscribed(user_id, context):
        update.message.reply_text(
            "⚠️ Подпишись на канал, чтобы использовать бота:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL[1:]}")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ])
        )
        return

    text = update.message.text
    if "tiktok.com" in text:
        download_tiktok(update, context)
    elif "instagram.com" in text:
        download_instagram(update, context)
    else:
        update.message.reply_text("❌ Отправь ссылку TikTok или Instagram")

def download_tiktok(update: Update, context: CallbackContext):
    try:
        url = update.message.text
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()
        
        video_url = response['data']['play']
        update.message.reply_video(
            video=video_url,
            caption=f"🎥 Видео скачано!\nПодпишись: {CHANNEL}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {str(e)}")

def download_instagram(update: Update, context: CallbackContext):
    try:
        url = update.message.text
        api_url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
        params = {"url": url}
        
        response = requests.get(api_url, params=params).json()
        video_url = response['media']
        
        update.message.reply_video(
            video=video_url,
            caption=f"📸 Видео скачано!\nПодпишись: {CHANNEL}"
        )
    except:
        update.message.reply_text("❌ Не удалось загрузить видео")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "check_sub":
        if is_subscribed(query.from_user.id, context):
            query.answer("✅ Теперь можешь отправлять ссылки!")
            query.edit_message_text("✔️ Подписка подтверждена! Отправь ссылку")
        else:
            query.answer("😢 Ты ещё не подписался", show_alert=True)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
