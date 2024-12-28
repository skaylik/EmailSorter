import telebot
from telebot import types
import config
import func

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # разметка клавиатуры
    btn1 = types.KeyboardButton('Проверить наличие работ и загрузить их')  
    markup.add(btn1)
    btn2 = types.KeyboardButton('Удалить эти письма')  
    markup.add(btn2)
    bot.send_message(chat_id, 'Привет! Добро пожаловать в бота сортировщика писем!', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)

def on_click(message):
    if message.text == 'Проверить наличие работ и загрузить их':
        check_emails(message)
    elif message.text == 'Удалить эти письма':
        delete_emails(message)

@bot.message_handler(commands=['check'])
def check_emails(message): 
    chat_id = message.chat.id
    imap = func.connection() 
    if imap:
        bot.send_message(chat_id, "Успешно подключено к почтовому серверу")
        imap.select("INBOX")
        deadlines = func.load_deadlines(config.file_deadlines)
        email_ids = func.fetch_emails(imap, deadlines)
        func.process_emails(imap, email_ids, chat_id, bot)
        imap.logout()

    bot.register_next_step_handler(message, on_click)

@bot.message_handler(commands=['delete'])
def delete_emails(message):
    chat_id = message.chat.id
    imap = func.connection()
    if imap:
        bot.send_message(chat_id, "Идет процесс удаления") 

        deadlines = func.load_deadlines(config.file_deadlines)
        email_ids = func.fetch_emails(imap, deadlines)

        func.delete_emails(imap, email_ids)
        bot.send_message(chat_id, 'Сообщения удалены!')

    bot.register_next_step_handler(message, on_click)

if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling()