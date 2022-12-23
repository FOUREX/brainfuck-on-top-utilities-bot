import sqlite3


conn = sqlite3.connect("db.sqlite")
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
            alerts_map_theme TEXT NOT NULL
        )""")

    conn.commit()


def new_user(chat_id: int, user_id: int, alerts_map_theme: str):
    cur.execute("INSERT INTO users VALUES (?, ?, ?)", (chat_id, user_id, alerts_map_theme))

    conn.commit()
