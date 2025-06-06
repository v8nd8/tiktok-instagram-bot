import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

TOKEN = "7240087170:AAEYeJrZyYPleAX0pwTRPwmW3dwKbe5GIog"  # твой токен бота
CHANNEL = "@mirznan1"  # твой канал

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=3000)

def keep_alive():
    t = Thread(target=run)
    t.start()

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

def get_tiktok_video(url):
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = {'url': url, 'format': '', 'token': ''}
    res = session.post('https://ttdownloader.com/req/', headers=headers, data=data)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        video_url = soup.find('a', attrs={'rel':'nofollow'})
        if video_url:
            return video_url['href']
    return None

def get_instagram_video(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        meta = soup.find('meta', property='og:video')
        if meta:
            return meta['content']
    return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Привет! Отправь ссылку на видео из TikTok или Instagram.\nНо сначала подпишись на канал {CHANNEL}.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, f"Ты должен подписаться на канал {CHANNEL}, чтобы пользоваться ботом.")
        return

    url = message.text.strip()
    if "tiktok.com" in url:
        bot.send_message(message.chat.id, "Ищу видео в TikTok...")
        video_url = get_tiktok_video(url)
        if video_url:
            bot.send_video(message.chat.id, video_url)
        else:
            bot.send_message(message.chat.id, "Не удалось получить видео из TikTok.")
    elif "instagram.com" in url:
        bot.send_message(message.chat.id, "Ищу видео в Instagram...")
        video_url = get_instagram_video(url)
        if video_url:
            bot.send_video(message.chat.id, video_url)
        else:
            bot.send_message(message.chat.id, "Не удалось получить видео из Instagram.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, пришли ссылку на видео из TikTok или Instagram.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
