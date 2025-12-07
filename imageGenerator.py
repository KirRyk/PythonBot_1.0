from telebot import TeleBot, types
import random
import requests
from urllib.parse import quote_plus

BOTTOKEN = "8327175837:AAE_PDIkfU1yOrMoGxx1vRFFcGj_zZ2kVAE"


bot = TeleBot(BOTTOKEN) #связь с ботом

@bot.message_handler(commands=["img"])
def sendImg(m):
    prompt = m.text.partition(' ')[2].strip()
    bot.send_message(m.chat.id, "Ищу...")
    seed = random.randint(0, 2_000_000_000)
    q = quote_plus(f"{prompt}, high quality, very detailed, soft light")
    url = f"https://image.pollinations.ai/prompt/{q}?width=1920&height=1080&seed={seed}&n=1"
    res = requests.get(url, timeout=90, allow_redirects=True)
    bot.send_photo(m.chat.id, res.content)


bot.infinity_polling()