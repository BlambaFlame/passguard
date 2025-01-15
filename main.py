import os
import dotenv

import telebot
from telebot import types
import telebot.formatting

from passwords import hash_master_password, generate_password
from models import save_user, get_users_all, get_account_pass

dotenv.load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

# Для хранения данных в json, пока нет базы данных
# При каждом выключении бота, что логично, чистится
users = {}

# Глобальный объект клавиатуры из одной кнопки "Назад"
back_keyboard = types.InlineKeyboardMarkup()
back_to_menu_key = types.InlineKeyboardButton('Назад', callback_data='back_to_menu_key')
back_keyboard.add(back_to_menu_key)


# Старт бота. Проверяет, зарегистрирован ли пользователь в базе данных.
# Если нет, просит ввести пароль для регистрации.
# Если да - сразу пускает в меню
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    ids = get_users_all()
    print(ids)
    if message.from_user.id not in ids:
        bot.send_message(chat_id, 'Привет! Я бот, который поможет тебе хранить пароли в безопасности. Давай зарегистрируемся. Введи пароль, который будешь использовать для разблокирования возможностей бота:')
        bot.register_next_step_handler(message, password_to_db)
    elif message.from_user.id in ids:
        bot.send_message(chat_id, 'Привет! Я бот, который поможет тебе хранить пароли в безопасности.')
        menu(message)


# В случае, если пользователь регистрируется, вызывает функцию password_to_db.
# Она отправляет ID из телеграма и хэшированный пароль в add_user, которая добавляет данные в бд
@bot.message_handler()
def password_to_db(message):
    chat_id = message.chat.id
    user_telegram_id = message.from_user.id
    password = hash_master_password(message.text)
    save_user(user_telegram_id, password)
    bot.send_message(chat_id, 'Пароль сохранен. Теперь ты можешь пользоваться ботом')
    menu(message)


# Хэндлер для вывода меню на команду /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    chat_id = message.chat.id

    # Создание объектов кнопок в меню бота
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    generate_password_key = types.InlineKeyboardButton('Сгенерировать пароль', callback_data='generate_password_key')
    search_login_by_resource_key = types.InlineKeyboardButton('Найти логин/пароль по названию ресурса', callback_data='search_login_by_resource_key')
    save_new_login_key = types.InlineKeyboardButton('Сохранить новый логин/пароль', callback_data='save_new_login_key')
    delete_login_key = types.InlineKeyboardButton('Удалить логин/пароль', callback_data='delete_login_key')

    # Привязка кнопок к меню
    keyboard.add(generate_password_key, search_login_by_resource_key)
    keyboard.add(save_new_login_key, delete_login_key)
    
    # Показ сообщения с кнопками
    bot.send_message(chat_id, 'Выберите пункт меню', reply_markup=keyboard)


# Хэндлер кнопки назад в клавиатуре back_keyboard
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_menu_key'))
def back_to_menu_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == "back_to_menu_key":
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.delete_message(chat_id, message_id)
            menu(call.message)
    except Exception as e:
        print(e)


# Хэндлер генерации нового пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('generate_password_key'))
def generate_password_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'generate_password_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(chat_id, "Введите название ресурса:")
            bot.register_next_step_handler(call.message, resource_to_generate)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)

def resource_to_generate(message):
    try:
        chat_id = message.chat.id
        message_id = message.message_id
        resource = message.text
        password = generate_password()
        if password:
            bot.send_message(chat_id, f"Ваш пароль от {resource}: {telebot.formatting.hcode(password)}", reply_markup=back_keyboard, parse_mode='HTML')
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)

# Хэндлер поиска пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('search_login_by_resource_key'))
def search_login_by_resource_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'search_login_by_resource_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            temp_message = bot.send_message(call.message.chat.id, "Введите название ресурса:")
            bot.delete_message(chat_id, message_id)
            bot.register_next_step_handler(call.message, search_login)
            #bot.delete_message(chat_id, temp_message.message_id)
    except Exception as e:
        print(e)

def search_login(message):
    try:
        chat_id = message.chat.id
        message_id = message.message_id
        user_id = message.from_user.id
        resource = message.text
        password = get_account_pass(user_id, resource)
        if password:
            bot.send_message(chat_id, f"Ваш пароль от {resource}: {telebot.formatting.hcode(password)}", reply_markup=back_keyboard, parse_mode='HTML')
            bot.delete_message(chat_id, message_id)
        elif not password:
            bot.send_message(chat_id, "Пароль не найден, попробуйте ещё раз:")
            bot.register_next_step_handler(message, search_login)
    except Exception as e:
        print(e)

# Хэндлер сохранения пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('save_new_login_key'))
def save_new_login_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'save_new_login_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Сохранение пока недоступно", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


# Хэндлер удаления пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_login_key'))
def delete_login_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'delete_login_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Удаление пока недоступно", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен")
    bot.infinity_polling()
