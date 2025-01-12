import telebot
from config import TOKEN
from telebot import types

bot = telebot.TeleBot(TOKEN)

# Для хранения данных в json, пока нет базы данных
# При каждом выключении бота, что логично, чистится
users = {}

# Глобальный объект клавиатуры из одной кнопки "Назад"
back_keyboard = telebot.types.InlineKeyboardMarkup()
back_to_menu_key = telebot.types.InlineKeyboardButton('Назад', callback_data='back_to_menu_key')
back_keyboard.add(back_to_menu_key)

# Хэндлер для регистрации пользователя, работает при
# отправке любого сообщения после команды /start
def save_username(message):
    chat_id = message.chat.id
    name = message.chat.first_name
    surname = message.chat.last_name
    users[chat_id]['name'] = name
    users[chat_id]['surname'] = surname
    bot.send_message(chat_id, "Вы зарегистрированы.")

# Тестовый хэндлер для вывода имени и фамилии зарегистрированного пользователя
@bot.message_handler(commands=['whoami'])
def whoami(message):
    chat_id = message.chat.id
    name = users[chat_id]['name']
    surname = users[chat_id]['surname']
    bot.send_message(chat_id, f'Ваше имя: {name} {surname}')

# Хэндлер для вывода меню на команду /menu или при старте бота
@bot.message_handler(commands=['menu', "start"])
def menu(message):
    chat_id = message.chat.id

    # Создание объектов кнопок в меню бота
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    generate_password_key = telebot.types.InlineKeyboardButton('Сгенерировать пароль', callback_data='generate_password_key')
    search_login_by_resource_key = telebot.types.InlineKeyboardButton('Найти логин/пароль по названию ресурса', callback_data='search_login_by_resource_key')
    save_new_login_key = telebot.types.InlineKeyboardButton('Сохранить новый логин/пароль', callback_data='save_new_login_key')
    delete_login_key = telebot.types.InlineKeyboardButton('Удалить логин/пароль', callback_data='delete_login_key')
    view_all_logins_key = telebot.types.InlineKeyboardButton('Посмотреть список сохраненных паролей', callback_data='view_all_logins_key')
    export_or_import_logins_key = telebot.types.InlineKeyboardButton('Экспорт/Импорт сохраненных логинов', callback_data='export_or_import_logins_key')
    app_settings_key = telebot.types.InlineKeyboardButton('Настройки приложения', callback_data='app_settings_key')

    # Привязка кнопок к меню
    keyboard.add(generate_password_key, search_login_by_resource_key)
    keyboard.add(save_new_login_key, delete_login_key)
    keyboard.add(view_all_logins_key, export_or_import_logins_key)
    keyboard.add(app_settings_key)
    
    # Показ сообщения с кнопками
    bot.send_message(chat_id, 'Выберите пункт меню', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery) -> None:
    try:
        if call.data == "back_to_menu_key":
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.delete_message(chat_id, message_id)
            menu(call.message)
        if call.data == 'generate_password_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Генерация пока недоступна", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)

        if call.data == 'search_login_by_resource_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Поиск пока недоступен")

        if call.data == 'save_new_login_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Сохранение пока недоступно")

        if call.data == 'delete_login_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Удаление пока недоступно")

        if call.data == 'view_all_logins_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Просмотр пока недоступен")

        if call.data == 'export_or_import_logins_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Экспорт/Импорт пока недоступен")

        if call.data == 'app_settings_key':
            chat_id = call.message.chat.id
            bot.send_message(chat_id, "Настройки пока недоступны")

    except Exception as e:
        print(e)


if __name__ == '__main__':
    print("Бот запущен")
    bot.infinity_polling()