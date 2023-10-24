import sqlite3

from json import dumps, loads


conn = sqlite3.connect("db.db")
cur = conn.cursor()


def create_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS aliases(
        chat_id INT NOT NULL,
        alias TEXT UNIQUE NOT NULL,
        user_id INT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            chat_id INT NOT NULL,
            user_id INT NOT NULL,
            alerts_map_theme TEXT NOT NULL,
            data TEXT
        )""")

    conn.commit()


def new_user(chat_id: int, user_id: int, alerts_map_theme: str = "0", data: dict = None):
    data = dumps(data)

    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (chat_id, user_id, alerts_map_theme, data))
    conn.commit()


def update_user_data(chat_id: int, user_id: int, data: dict):
    cur.execute("UPDATE users SET data = ? WHERE chat_id = ? AND user_id = ?", (data, chat_id, user_id))
    conn.commit()
