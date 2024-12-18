# Менеджер паролей PassGuard

## Пользовательские сценарии

### Главный экран
	1.	Пользователь открывает приложение.
	2.	Система показывает меню с функциями:
	    - Сгенерировать новый пароль.
	    - Найти логин/пароль по названию ресурса.
	    - Сохранить логин/пароль для нового ресурса.
	    - Удалить сохраненные данные для ресурса.
	    - Посмотреть список сохраненных ресурсов.
	    - Экспортировать/импортировать пароли.
	    - Настройки приложения.

### Сценарий 1: Генерация нового пароля
	1.	Пользователь выбирает “Сгенерировать новый пароль”.
	2.	Система запрашивает параметры пароля:
	    - Длина (например, от 8 до 32 символов).
	    - Использование спецсимволов, цифр, заглавных/строчных букв.
	3.	Пользователь задает параметры.
	4.	Система генерирует пароль и отображает его на экране с предложением:
	    - Скопировать в буфер обмена.
	    - Сохранить пароль для ресурса.
	5.	Пользователь выбирает действие (например, сохранить для ресурса).

### Сценарий 2: Поиск логина/пароля
	1.	Пользователь выбирает “Найти логин/пароль”.
	2.	Система запрашивает название ресурса.
	3.	Пользователь вводит название ресурса.
	4.	Система:
	    - Если данные найдены, отображает логин и пароль.
	    - Если данных нет, сообщает: “Ресурс не найден”.

### Сценарий 3: Сохранение новых данных
	1.	Пользователь выбирает “Сохранить логин/пароль”.
	2.	Система запрашивает:
	    - Название ресурса.
	    - Логин.
	    - Пароль.
	3.	Пользователь вводит данные.
	4.	Система сохраняет их и подтверждает: “Данные успешно сохранены”.

### Сценарий 4: Удаление данных
	1.	Пользователь выбирает “Удалить сохраненные данные”.
	2.	Система запрашивает название ресурса.
	3.	Пользователь вводит название.
	4.	Система:
	    - Если данные найдены, удаляет их и сообщает: “Данные удалены”.
	    - Если данных нет, сообщает: “Ресурс не найден”.

### Сценарий 5: Просмотр списка ресурсов
	1.	Пользователь выбирает “Посмотреть список сохраненных ресурсов”.
	2.	Система отображает список всех сохраненных ресурсов (без логинов и паролей).
	3.	Пользователь может выбрать ресурс для отображения логина/пароля.

### Сценарий 6: Экспорт/импорт паролей
	1.	Пользователь выбирает “Экспортировать/импортировать пароли”.
	2.	Система предлагает два действия:
	    - Экспорт паролей в файл (с установкой пароля на файл).
	    - Импорт паролей из файла.
	3.	Пользователь выбирает действие:
	    - Для экспорта: файл сохраняется с шифрованием.
	    - Для импорта: система запрашивает файл и пароль, затем импортирует данные.

### Сценарий 7: Настройки
	1.	Пользователь выбирает “Настройки”.
	2.	Система показывает доступные параметры:
	    - Изменение главного пароля приложения.
	    - Настройка безопасности (например, двухфакторная аутентификация, автозавершение сеанса).
	    - Темы и оформление.
	    - Управление хранилищем данных (локально/в облаке).
	3.	Пользователь изменяет нужные настройки.

### Общие сценарии (ошибки и уведомления)
	    - Неверный ввод данных: если пользователь вводит некорректные данные (например, пустое поле), система сообщает об ошибке и просит повторить ввод.
	    - Сессия истекла: если пользователь неактивен определенное время, приложение автоматически завершает сеанс для защиты данных.