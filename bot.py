from telebot import TeleBot, types
import threading
from datetime import datetime
import time
import pandas
import random
import requests
from urllib.parse import quote_plus

BOTTOKEN = "8327175837:AAE_PDIkfU1yOrMoGxx1vRFFcGj_zZ2kVAE"

bot = TeleBot(BOTTOKEN) #связь с ботом

users = set() # Множество chat.id, подписавшихся на уведомления

days_of_week = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}

@bot.message_handler(commands=['start'])
def cmdStart(m):
    bot.send_sticker(m.chat.id, "CAACAgIAAxkBAAEP2slpI0DrHa3__oA7XIca2GC9IVneDgACAUMAAvPmMEpciaGmXWWHBzYE")
    bot.send_message(m.chat.id, "Привет! \n"
                     "Напиши /info для продолжения")

@bot.message_handler(commands=['info'])
def cmdInfo(m):
    klava1 = types.InlineKeyboardMarkup()
    klava2 = types.ReplyKeyboardMarkup()

    btn1 = types.InlineKeyboardButton('/notice', callback_data='notice')
    btn2 = types.InlineKeyboardButton('/unsub', callback_data='unsub')
    btn3 = types.InlineKeyboardButton('/image', callback_data='image')
    btn4 = types.InlineKeyboardButton('/parser', callback_data='parser')

    btn5 = types.KeyboardButton('/notice')
    btn6 = types.KeyboardButton('/unsub')
    btn7 = types.KeyboardButton('/image')
    btn8 = types.KeyboardButton('/parser')

    klava1.add(btn1, btn2, btn3, btn4)
    klava2.add(btn5, btn6, btn7, btn8)

    bot.send_message(m.chat.id, 'Список команд 🍽🍽️👹', reply_markup=klava1)
    bot.send_message(m.chat.id, '/start - приветствие \n'
                                '/info - меню бота \n'
                                '\n'
                                '/notice - подисаться на уведомления \n'
                                '/unsub - отписаться от уведомлений \n'
                                '/image - генератор изображений \n'
                                '/parser - подборка товаров электроники', reply_markup=klava2)



@bot.message_handler(commands=["image"])
def sendImg(m):
    prompt = m.text.partition(' ')[2].strip()
    bot.send_message(m.chat.id, "Ищу...")
    seed = random.randint(0, 2_000_000_000)
    q = quote_plus(f"{prompt}, high quality, very detailed, soft light")
    url = f"https://image.pollinations.ai/prompt/{q}?width=1920&height=1080&seed={seed}&n=1"
    res = requests.get(url, timeout=90, allow_redirects=True)
    bot.send_photo(m.chat.id, res.content)


@bot.message_handler(commands=['notice'])
def cmdNotice(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, "Теперь вы будете получать уведомления из расписания 👹👹")

@bot.message_handler(commands=['unsub'])
def cmdUnsub(m):
    users.discard(m.chat.id)
    bot.send_message(m.chat.id, "Вы отписались от уведомлений 👹👹👹👹👹👹👹")

def setNotification(user):
    today_weekday = 3 #datetime.today().weekday() + 1

    if today_weekday == 6 or today_weekday == 7:
        bot.send_message(user, "Сегодня выходной, ура! Ты выжил! Но не расслабляйся: через мгновенье эта нечисть вновь придёт - понедельник...")

    df = pandas.read_excel("shedule.xlsx")

    today_schedule = df[df['День'] == today_weekday]
    responce = f'Расписание на {days_of_week[today_weekday]}'

    for _, row in today_schedule.iterrows():
        responce += "▫️" * 20 + "\n"

        for column, value in row.items():
            if column != 'День' and pandas.notna(value) and str(value).strip() != '':
                column_name = column
                responce += f"*{column_name}:* {value}\n"

        responce += "\n" + "═" * 30 + "\n\n"

    total_lessons = len(today_schedule)
    responce += f"📊 *Всего пар: {total_lessons}*"

    bot.send_message(user, responce)

def check_time():
    while True:
        now = datetime.now()
        if now.hour == 20 and now.minute == 58 or now.hour == 7 and now.minute == 0:
            for user in list(users):
                setNotification(user)
            time.sleep(65)
        else:
            time.sleep(10)


def notification():
    scheduler_thread = threading.Thread(target=check_time)
    scheduler_thread.daemon = True # Фоновый поток
    scheduler_thread.start()


if __name__ == "__main__":
    print("Бот запущен...")
    notification()  # Запуск фоновых уведомлений
    bot.infinity_polling()

