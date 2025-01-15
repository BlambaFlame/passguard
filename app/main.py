import os
import dotenv

import telebot
from telebot import types

from passwords import hash_master_password
from models import save_user, get_users_all, save_account_pass, get_user_accounts_all, get_account_pass, Account, delete_account_pass

dotenv.load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

# Для хранения данных в json, пока нет базы данных
# При каждом выключении бота, что логично, чистится
users = {}
user_states = {}

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
        user_states[chat_id] = 'waiting_for_password'
    elif message.from_user.id in ids:
        bot.send_message(chat_id, 'Привет! Я бот, который поможет тебе хранить пароли в безопасности.')
        menu(message)


# Хэндлер для вывода меню на команду /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    chat_id = message.chat.id

    # Создание объектов кнопок в меню бота
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    search_login_by_resource_key = types.InlineKeyboardButton('Найти логин/пароль по названию ресурса', callback_data='search_login_by_resource_key')
    save_new_login_key = types.InlineKeyboardButton('Сохранить новый логин/пароль', callback_data='save_new_login_key')
    delete_login_key = types.InlineKeyboardButton('Удалить логин/пароль', callback_data='delete_login_key')
    view_all_logins_key = types.InlineKeyboardButton('Посмотреть список сохраненных паролей', callback_data='view_all_logins_key')
    export_or_import_logins_key = types.InlineKeyboardButton('Экспорт/Импорт сохраненных логинов', callback_data='export_or_import_logins_key')
    app_settings_key = types.InlineKeyboardButton('Настройки приложения', callback_data='app_settings_key')

    # Привязка кнопок к меню
    keyboard.add(search_login_by_resource_key)
    keyboard.add(save_new_login_key, delete_login_key)
    keyboard.add(view_all_logins_key, export_or_import_logins_key)
    keyboard.add(app_settings_key)
    
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


# Хэндлер поиска пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('search_login_by_resource_key'))
def search_login_by_resource_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'search_login_by_resource_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Поиск пока недоступен", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


# Хэндлер для сохранения пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('save_new_login_key'))
def save_new_login_key(call: types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Уведомляем пользователя о начале процесса сохранения
    bot.send_message(chat_id, "Пожалуйста, введите название сервиса:")

    # Устанавливаем состояние пользователя
    user_states[chat_id] = {'step': 'service_name'}

    # Удаляем предыдущее сообщение
    bot.delete_message(chat_id, message_id)

# Хэндлер для обработки текстовых сообщений и callback'ов
@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_user_input(message: types.Message) -> None:
    chat_id = message.chat.id
    state = user_states[chat_id]

    if state == 'waiting_for_password':
        password = hash_master_password(message.text)
        save_user(message.from_user.id, password)
        bot.send_message(chat_id, 'Пароль сохранен. Теперь ты можешь пользоваться ботом.')
        del user_states[chat_id]
        menu(message)

    elif state['step'] == 'service_name':
        # Сохраняем название сервиса
        service_name = message.text
        state['service_name'] = service_name

        # Запрашиваем логин
        bot.send_message(chat_id, "Теперь введите логин:")
        state['step'] = 'login'

    elif state['step'] == 'login':
        # Сохраняем логин
        login = message.text
        state['login'] = login

        # Запрашиваем пароль
        bot.send_message(chat_id, "Теперь введите пароль:")
        state['step'] = 'password'

    elif state['step'] == 'password':
        # Сохраняем пароль и вызываем метод сохранения
        password = message.text

        tg_uid = message.from_user.id  # Получаем Telegram ID пользователя
        service_name = state.get('service_name')
        login = state.get('login')

        # Сохраняем аккаунт и пароль в базе данных
        save_account_pass(tg_uid, service_name, login, password)

        # Уведомляем пользователя об успешном добавлении аккаунта
        bot.send_message(chat_id, "Аккаунт успешно добавлен!")

        # Удаляем состояние пользователя после завершения процесса
        del user_states[chat_id]
        menu(message)


# Хэндлер удаления пароля
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_login_key'))
def delete_login_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'delete_login_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            # Получаем все аккаунты пользователя
            tg_uid = call.from_user.id
            accounts = get_user_accounts_all(tg_uid)  # Получаем список аккаунтов

            keyboard = types.InlineKeyboardMarkup()  # Создаем клавиатуру

            if accounts:  # Проверяем, есть ли аккаунты
                for account_id, account_source, login in accounts:
                    # Создаем кнопку для каждого аккаунта с текстом "Удалить Аккаунт: логин"
                    button_text = f"Удалить {account_source}: {login}"
                    button = types.InlineKeyboardButton(button_text, callback_data=f'confirm_delete_{account_id}')
                    keyboard.add(button)

                bot.send_message(chat_id, "Выберите аккаунт для удаления:", reply_markup=keyboard)
            else:
                bot.send_message(chat_id, "У вас нет сохраненных аккаунтов.", reply_markup=back_keyboard)

            # Удаляем предыдущее сообщение
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_handler(call: types.CallbackQuery) -> None:
    try:
        # Получаем ID аккаунта из callback_data
        account_id = call.data.split('_')[2]
        tg_uid = call.from_user.id

        # Получаем источник аккаунта для отображения в сообщении
        account_source = Account.get(Account.id == account_id).account_source

        # Запрашиваем подтверждение у пользователя
        keyboard = types.InlineKeyboardMarkup()
        confirm_button = types.InlineKeyboardButton("Да", callback_data=f'delete_account_{account_id}')
        cancel_button = types.InlineKeyboardButton("Нет", callback_data='cancel_delete')
        keyboard.add(confirm_button, cancel_button)

        bot.send_message(call.message.chat.id, f"Вы уверены, что хотите удалить аккаунт {account_source}?", reply_markup=keyboard)

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_account_'))
def delete_account_handler(call: types.CallbackQuery) -> None:
    try:
        # Получаем ID аккаунта из callback_data
        account_id = call.data.split('_')[2]
        tg_uid = call.from_user.id

        # Получаем источник аккаунта для удаления
        account_source = Account.get(Account.id == account_id).account_source

        # Удаляем аккаунт
        delete_account_pass(account_id)

        # Уведомляем пользователя об успешном удалении
        bot.send_message(call.message.chat.id, f"Аккаунт {account_source} успешно удален.", reply_markup=back_keyboard)

        # Обновляем список аккаунтов после удаления
        delete_login_key(call)  # Вызываем функцию для показа обновленного списка

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_delete')
def cancel_delete_handler(call: types.CallbackQuery) -> None:
    try:
        bot.send_message(call.message.chat.id, "Удаление отменено.", reply_markup=back_keyboard)
    except Exception as e:
        print(e)


# Хэндлер просмотра списка паролей
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_all_logins_key'))
def view_all_logins_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'view_all_logins_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            tg_uid = call.from_user.id

            # Получаем все аккаунты пользователя
            accounts = get_user_accounts_all(tg_uid)  # Получаем список аккаунтов

            keyboard = types.InlineKeyboardMarkup()  # Создаем клавиатуру

            if accounts:  # Проверяем, есть ли аккаунты
                for account_id, account_source, login in accounts:
                    # Создаем кнопку для каждого аккаунта с текстом "Аккаунт: логин"
                    button_text = f"{account_source}: {login}"
                    button = types.InlineKeyboardButton(button_text, callback_data=f'account_info_{account_id}')
                    keyboard.add(button)

                bot.send_message(chat_id, "Выберите аккаунт:", reply_markup=keyboard)
            else:
                bot.send_message(chat_id, "У вас нет сохраненных аккаунтов.", reply_markup=back_keyboard)

            # Удаляем предыдущее сообщение
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('account_info_'))
def account_info_handler(call: types.CallbackQuery) -> None:
    try:
        # Получаем ID аккаунта из callback_data
        account_id = call.data.split('_')[2]
        tg_uid = call.from_user.id

        # Получаем информацию о пароле для выбранного аккаунта
        account_source = Account.get(Account.id == account_id).account_source
        login, password_info = get_account_pass(tg_uid, account_source)

        # Отправляем информацию пользователю
        bot.send_message(call.message.chat.id, f"Информация об аккаунте {account_source}:\nЛогин: {login}\nПароль: {password_info}", reply_markup=back_keyboard)

    except Exception as e:
        print(f"Ошибка в хэндлере account_info_handler: {e}")


# Хэндлер экспорта/импорта
@bot.callback_query_handler(func=lambda call: call.data.startswith('export_or_import_logins_key'))
def export_or_import_logins_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'export_or_import_logins_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Экспорт и импорт пока недоступен", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


# Хэндлер настроек бота
@bot.callback_query_handler(func=lambda call: call.data.startswith('app_settings_key'))
def app_settings_key(call: types.CallbackQuery) -> None:
    try:
        if call.data == 'app_settings_key':
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            bot.send_message(call.message.chat.id, "Настройки пока недоступны", reply_markup=back_keyboard)
            bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен")
    bot.infinity_polling()
