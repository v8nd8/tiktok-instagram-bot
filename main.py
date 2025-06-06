import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Настройки
TOKEN = '7240087170:AAEYeJrZyYPleAX0pwTRPwmW3dwKbe5GIog'  # Твой токен
CHANNEL = '@mirznan1'  # Твой канал (начинается с @)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка подписки
def check_subscription(user_id: int, context: CallbackContext) -> bool:
    try:
        member = context.bot.get_chat_member(CHANNEL[1:], user_id)  # Убираем @
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n"
        f"📤 Присылай ссылку из TikTok или Instagram, и я скачаю видео.\n"
        f"📢 Подпишись на канал: {CHANNEL}"
    )

# Обработчик сообщений
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if not check_subscription(user_id, context):
        update.message.reply_text(
            "⚠️ Подпишись на канал, чтобы использовать бота:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL[1:]}")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ])
        )
        return

    url
