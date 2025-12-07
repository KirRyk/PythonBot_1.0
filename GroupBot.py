from telebot import  TeleBot, types

BOTTOKEN = "8327175837:AAE_PDIkfU1yOrMoGxx1vRFFcGj_zZ2kVAE"

badword = "гол гооооол гоооооолыыыыы"

bot = TeleBot(BOTTOKEN)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def control(m: types.Message):
    if m.text in badword:
        bot.delete_message(m.chat.id, m.message_id)
    if m.text == "hi":
        bot.send_message(m.chat.id, "hiiii")

bot.infinity_polling()