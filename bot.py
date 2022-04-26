import logging
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from config import config
from datetime import datetime


connection = sqlite3.connect("db.sql")
cursor = connection.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id TEXT,
    name TEXT,
    aliases TEXT
)""")
connection.commit()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config["token"])
dp = Dispatcher(bot)
aliases = {}
chat_id = -1001622038758


def command(message: types.Message, command: str, permissions: str = "all"): # Работает - не трогай
    check = message.text.lower()[:len(command)+len(config["prefix"])] == config["prefix"] + command
   
    match permissions:
        case "all":
            return check
        case "dev":
            return check and message.from_user.id == 991921147


async def load_aliases(*args): # Работает - не трогай
    global aliases
    chat = await bot.get_chat(chat_id)
    members_count = await chat.get_member_count()

    users = cursor.execute("SELECT * FROM users").fetchmany(members_count)
    for user in users:
        for aliace in user[2].split():
            aliases.update({aliace: user[0]})


@dp.message_handler(commands=["help"]) # Работает - не трогай
async def help(message):
    p = config["prefix"]
    await message.answer(f"*Алиасы*\nАлиас - с англ. псевдоним.\n`{p}Добавить алиас` -> добавляет алиас.\n`{p}Алиасы` -> показывает ваши алиасы или пользователя на чьё сообщение вы ответили.\n`{p}Создать алиас`\\* -> создаёт алиас для пользователя.", parse_mode="Markdown")


@dp.message_handler(lambda message: command(message, "yep", "all")) # Работает - не трогай
async def yep(message: types.Message):
    await message.answer(f"{message.chat}")
    await message.answer(f"{type(message.chat)}")


@dp.message_handler(lambda message: command(message, "создать алиас", "dev")) # Работает - не трогай
async def create_alias(message: types.Message):
    id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.full_name
    alias = message.text.lower().split()[2].replace("(", "").replace(")", "") + " "

    if cursor.execute(f"SELECT * FROM users WHERE id = {id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ({id}, \"{name}\", \"{alias}\")")
    else:
        user_aliases = cursor.execute(f"SELECT aliases FROM users WHERE id = {id}").fetchone()[0]
        user_aliases += alias
        cursor.execute(f"UPDATE users SET aliases = \"{user_aliases}\" WHERE id = {id}")

    connection.commit()
    await load_aliases()

    await message.reply("Алиас добавлен")


@dp.message_handler(lambda message: command(message, "добавить алиас", "all")) # Работает - не трогай
async def new_aliase(message: types.Message):
    try:
        id = message.from_user.id
        name = message.from_user.username
        alias = message.text.lower().split()[2].replace("(", "").replace(")", "") + " "
    
        if cursor.execute(f"SELECT * FROM users WHERE id = {id}").fetchone() is None:
            cursor.execute(f"INSERT INTO users VALUES ({id}, \"{name}\", \"{alias}\")")
        else:
            user_aliases = cursor.execute(f"SELECT aliases FROM users WHERE id = {id}").fetchone()[0]
            user_aliases += alias
            cursor.execute(f"UPDATE users SET aliases = \"{user_aliases}\" WHERE id = {id}")

        connection.commit()
        await load_aliases()
        await message.reply("Алиас добавлен")
        
    except Exception as e:
        print(f"[{str(datetime.now().time()).split('.')[0]}]: {e}")


@dp.message_handler(lambda message: command(message, "алиасы", "all")) # Работает - не трогай
async def user_aliases(message: types.Message):
    try:
        if message.reply_to_message:
            id = message.reply_to_message.from_user.id
            name = message.reply_to_message.from_user.full_name
        else:
            id = message.from_user.id
            name = message.from_user.full_name

        user_aliases = cursor.execute(f"SELECT aliases FROM users WHERE id = {id}").fetchone()[0]
        
        text = ""
        for i, user_aliase in enumerate(user_aliases.split()):
            text += f"{i}: {user_aliase}\n"

        await message.answer(text)
    except:
        await message.answer("Нету алиасов")


@dp.message_handler() # Работает - не трогай
async def aliase(message: types.Message):
    for key in aliases:
        if key+"()" in message.text.lower().replace(" ", "").split():
            user = await bot.get_chat_member(chat_id, aliases[key])
            await message.reply(f"[{user.user.first_name}](tg://user?id={user.user.id})", parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=load_aliases)
