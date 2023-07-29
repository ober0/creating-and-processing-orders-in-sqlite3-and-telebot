import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot("6184823844:AAE7JvBRB4shgFkLd2353I9ihWf4Ggtkr74")

vip = None
id = None
srok = None
text = None



@bot.message_handler(commands=['help'])
def help(message):
    text = '''
/add - добавить обраение
/check - посмотерть открытые обращения  
/check_work - посмотерть обращения в работе
/check_close - посмотерть закрытые обращения  
Все обращения показываются в порядке возрастания срока заказа, так же вип в приоритете
    '''
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "isVip? (True/False)")
    bot.register_next_step_handler(message, add_step2)

def add_step2(message):
    global vip
    if message.text == 'True' or message.text == 'False':
        if message.text == 'True':
            vip = 0
        else:
            vip = 1
        bot.send_message(message.chat.id, "Телеграм Id")
        bot.register_next_step_handler(message, add_step3)
    else:
        bot.send_message(message.chat.id, 'Не корректное значение, Введите повторно:')
        bot.register_next_step_handler(message, add_step2)


def add_step3(message):
    global id
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Не корректный id, Введите повторно:')
        bot.register_next_step_handler(message, add_step3)
    else:
        id = message.text
        bot.send_message(message.chat.id, "Срок выполнения (в днях)")
        bot.register_next_step_handler(message, add_step4)

def add_step4(message):
    global srok
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Не корректный id, Введите повторно:')
        bot.register_next_step_handler(message, add_step4)
    else:
        srok = message.text

        db = sqlite3.connect("sqlite_zakaz.db")
        cursor = db.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS zakaz (
               vip integer,
               id integer,
               srok integer,
               status text  
           )
           """)

        cursor.execute(f"INSERT INTO zakaz VALUES ({vip}, {id}, {srok}, 'Открыт')")
        db.commit()
        db.close()
        bot.send_message(message.chat.id, "Обращение создано")


@bot.message_handler(commands=['check'])
def check(message):
    try:
        db = sqlite3.connect("sqlite_zakaz.db")
        cursor = db.cursor()

        cursor.execute("SELECT rowid, * FROM zakaz WHERE status = 'Открыт' ORDER BY vip, srok")


        text = cursor.fetchone()
        print(text)
        if text[1] == 0:
            user_vip = True
        else:
            user_vip = False

        viv = f'''
        Номер обращения: {text[0]}
        vip: {user_vip}
        id: {text[2]}
        Срок заказа: {text[3]} дней
        Статус: {text[4]}'''

        bot.send_message(message.chat.id, f'{viv}\n')

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton(text="В работе", callback_data='1')
        btn2 = types.InlineKeyboardButton(text="Закрыть", callback_data='2')
        btn3 = types.InlineKeyboardButton(text="Удалить", callback_data='3')
        markup.add(btn1, btn2, btn3)

        bot.send_message(message.chat.id, "Действие:", reply_markup=markup)
        db.close()
    except:
        bot.send_message(message.chat.id, 'Нет открытых обращений')

@bot.message_handler(commands=['check_work'])
def check2(message, ok = False):
    db = sqlite3.connect("sqlite_zakaz.db")
    cursor = db.cursor()

    cursor.execute("SELECT rowid, * FROM zakaz WHERE status = 'В работе' ORDER BY vip, srok")

    for i in cursor.fetchall():
        if i[1] == 0:
            user_vip = True
        else:
            user_vip = False

        viv = f'''
            Номер обращения: {i[0]}
            vip: {user_vip}
            id: {i[2]}
            Срок заказа: {i[3]} дней
            Статус: {i[4]}'''

        bot.send_message(message.chat.id, f'{viv}\n')
        ok = True

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn2 = types.InlineKeyboardButton(text="Закрыть", callback_data='2')
        btn3 = types.InlineKeyboardButton(text="Удалить", callback_data='3')
        markup.add(btn2, btn3)

        bot.send_message(message.chat.id, "Действие:", reply_markup=markup)
        db.close()
    if not ok:
        bot.send_message(message.chat.id, 'Нет обращений в работе')

@bot.message_handler(commands=['check_close'])
def check1(message, ok = False):
    db = sqlite3.connect("sqlite_zakaz.db")
    cursor = db.cursor()

    cursor.execute("SELECT rowid, * FROM zakaz WHERE status = 'Закрыт' ORDER BY vip, srok")

    for i in cursor.fetchall():
        if i[1] == 0:
            user_vip = True
        else:
            user_vip = False

        viv = f'''
            Номер обращения: {i[0]}
            vip: {user_vip}
            id: {i[2]}
            Срок заказа: {i[3]} дней
            Статус: {i[4]}'''

        bot.send_message(message.chat.id, f'{viv}\n')
        ok = True

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn2 = types.InlineKeyboardButton(text="В работе", callback_data='1')
        btn3 = types.InlineKeyboardButton(text="Удалить", callback_data='3')
        markup.add(btn2, btn3)

        bot.send_message(message.chat.id, "Действие:", reply_markup=markup)
        db.close()
    if not ok:
        bot.send_message(message.chat.id, 'Нет закрытых обращений')
def call1(message):
    db = sqlite3.connect("sqlite_zakaz.db")
    cursor = db.cursor()
    cursor.execute(f"UPDATE zakaz SET status = 'В работе' WHERE rowid = {message.text}")
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "Успешно")

def call2(message):
    db = sqlite3.connect("sqlite_zakaz.db")
    cursor = db.cursor()
    cursor.execute(f"UPDATE zakaz SET status = 'Закрыт' WHERE rowid = {message.text}")
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "Успешно")

def call3(message):
    db = sqlite3.connect("sqlite_zakaz.db")
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM zakaz WHERE rowid = {message.text}")
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "Успешно")

@bot.callback_query_handler(func=lambda callback: True)
def callback(callback):
    if callback.data == '1':
        bot.send_message(callback.message.chat.id, "Номер обращения:")
        bot.register_next_step_handler(callback.message, call1)

    if callback.data == '2':
        bot.send_message(callback.message.chat.id, "Номер обращения:")
        bot.register_next_step_handler(callback.message, call2)

    if callback.data == '3':
        bot.send_message(callback.message.chat.id, "Номер обращения:")
        bot.register_next_step_handler(callback.message, call3)



bot.polling(none_stop=True)