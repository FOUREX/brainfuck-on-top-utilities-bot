import logging

from aiogram import Bot, Dispatcher, executor, types
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from datetime import datetime


client = AsyncIOMotorClient(config["db"])
db = client["db"]
users = db["users"]


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config["token"])
dp = Dispatcher(bot)

aliases = {}
chat_id = -1001622038758


def debug(obj: object):
    if config["debug"] is True:
        print(obj)


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

    documents = await users.find().to_list(length=members_count)

    try:
        for document in documents:
            for aliase in document["aliases"]:
                aliases.update({aliase: document["id"]})
    except Exception as e:
        debug(e)


@dp.message_handler(commands=["help"]) # Работает - не трогай
async def help(message):
    p = config["prefix"]
    await message.answer(f"*Алиасы*\nАлиас - с англ. псевдоним.\n`{p}Добавить алиас` -> добавляет алиас.\n`{p}Алиасы` -> показывает ваши алиасы или пользователя на чьё сообщение вы ответили.\n`{p}Создать алиас`\\* -> создаёт алиас для пользователя.", parse_mode="Markdown")


@dp.message_handler(lambda message: command(message, "добавить алиас*", "dev")) # Работает - не трогай
async def new_aliase_dev(message: types.Message):
    id = message.reply_to_message.from_user.id
    name = message.reply_to_message.from_user.full_name
    alias = message.text.lower().split()[2].replace("(", "").replace(")", "")

    if await users.find_one({"id": id}) is None:
        await users.insert_one({"id": id, "name": name, "aliases": [alias]})
    else:
        user_aliases = (await users.find_one({"id": id}))["aliases"]
        user_aliases.append(alias)
        await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

    await load_aliases()
    await message.reply("Алиас добавлен")


@dp.message_handler(lambda message: command(message, "добавить алиас", "all")) # Работает - не трогай
async def new_aliase(message: types.Message):
    try:
        id = message.from_user.id
        name = message.from_user.username
        alias = message.text.lower().split()[2].replace("(", "").replace(")", "")
    
        if await users.find_one({"id": id}) is None:
            await users.insert_one({"id": id, "name": name, "aliases": [alias]})
        else:
            user_aliases = (await users.find_one({"id": id}))["aliases"]
            user_aliases.append(alias)
            await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

        await load_aliases()
        await message.reply("Алиас добавлен")
        
    except Exception as e:
        print(f"[{str(datetime.now().time()).split('.')[0]}]: {e}")


@dp.message_handler(lambda message: command(message, "удалить алиас*", "dev")) # Работает - не трогай
async def delete_aliase_dev(message: types.Message):
    id = message.reply_to_message.from_user.id
    index = int(message.text.lower().split()[2])

    try:
        user_aliases = (await users.find_one({"id": id}))["aliases"]
        user_aliases.pop(index)
        await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

        await message.reply("Алиас удалён")
    except Exception as e:
        debug(e)


@dp.message_handler(lambda message: command(message, "удалить алиас", "all")) # Работает - не трогай
async def delete_aliase(message: types.Message):
    id = message.from_user.id
    index = int(message.text.lower().split()[2])

    try:
        user_aliases = (await users.find_one({"id": id}))["aliases"]
        user_aliases.pop(index)
        await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

        await message.reply("Алиас удалён")
    except Exception as e:
        debug(e)


@dp.message_handler(lambda message: command(message, "алиасы", "all")) # Работает - не трогай
async def user_aliases(message: types.Message):
    try:
        if message.reply_to_message:
            id = message.reply_to_message.from_user.id
        else:
            id = message.from_user.id

        user_aliases = (await users.find_one({"id": id}))["aliases"]
        
        text = ""
        for i, user_aliase in enumerate(user_aliases):
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