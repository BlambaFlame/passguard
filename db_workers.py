import sqlite3 as sqlite

connection = sqlite.connect('db/database.sqlite3', check_same_thread=False)
with connection:
    data = connection.execute("select count(*) from sqlite_master where type='table' and name='users'")
    for row in data:
        if row[0] == 0:
            with connection:
                connection.execute("""
                                CREATE TABLE users (
                                user_telegram_id PRIMARY_KEY INTEGER UNIQUE NOT NULL,
                                user_password TEXT NOT NULL);
                                """)

def add_user(user_telegram_id, user_password):
    with connection:
        connection.execute("""
                        INSERT INTO users (user_telegram_id, user_password)
                        VALUES (?, ?);
                        """, (user_telegram_id, user_password))
        
def get_all_users():
    with connection:
        connection.row_factory = lambda cursor, row: row[0]
        c = connection.cursor()
        ids = c.execute('SELECT user_telegram_id FROM users').fetchall()
        return ids
