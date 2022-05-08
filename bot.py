import logging

from aiogram import Bot, Dispatcher, executor, types
from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from datetime import datetime
from alerts import get_alerts
from psutil import virtual_memory, cpu_percent


client = AsyncIOMotorClient(config["db"])
db = client["db"]
users = db["users"]


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config["token"])
dp = Dispatcher(bot)

aliases = {}
chat_id = -1001622038758
start_time = datetime.now()


def debug(obj: object): # Работает - не трогай
    if config["debug"] is True:
        print(obj)


def command(message: types.Message, command: str, permissions: str = "all"): # Работает - не трогай
    command = command + "*" if permissions == "dev" else command
    check = message.text.lower()[:len(command)+len(config["prefix"])] == config["prefix"] + command
   
    match permissions:
        case "all":
            return check
        case "dev":
            return check and message.from_user.id == 991921147


def _help(**kwargs): # Работает - не трогай
    def wrapper(*args):
            kwargs.update({"command": config["prefix"] + kwargs["command"]})
            if kwargs["permissions"] == "dev":
                kwargs.update({"command": kwargs["command"] + "*"})
            else:
                pass
            
            return kwargs

    return wrapper


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


class Aliases: # Работает - не трогай
    @classmethod
    def commands(cls):
        return [
            cls.new_aliase_dev, cls.new_aliase,  # type: ignore
            cls.delete_aliase_dev, cls.delete_aliase,  # type: ignore
            cls.user_aliases  # type: ignore
        ]


    @_help(
        command = f"Новый алиас",
        args = {"алиас": "str"},
        description = "Добавляет алиас пользователю.",
        permissions = "dev"
    )
    @dp.message_handler(lambda message: command(message, "новый алиас", "dev")) # Работает - не трогай
    async def new_aliase_dev(message: types.Message):  # type: ignore
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


    @_help(
        command = f"Новый алиас",
        args = {"алиас": "str"},
        description = "Добавляет ваш алиас.",
        permissions = "all"
    )
    @dp.message_handler(lambda message: command(message, "новый алиас", "all")) # Работает - не трогай
    async def new_aliase(message: types.Message):  # type: ignore
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


    @_help(
        command = f"Удалить алиас",
        args = {"индекс": "int"},
        description = "Удаляет алиас у пользователя.",
        permissions = "dev"
    )
    @dp.message_handler(lambda message: command(message, "удалить алиас", "dev")) # Работает - не трогай
    async def delete_aliase_dev(message: types.Message):  # type: ignore
        id = message.reply_to_message.from_user.id
        index = int(message.text.lower().split()[2])

        try:
            user_aliases = (await users.find_one({"id": id}))["aliases"]
            user_aliases.pop(index)
            await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

            await message.reply("Алиас удалён")
        except Exception as e:
            debug(e)


    @_help(
        command = f"Удалить алиас",
        args = {"индекс": "int"},
        description = "Удаляет ваш алиас.",
        permissions = "all"
    )
    @dp.message_handler(lambda message: command(message, "удалить алиас", "all")) # Работает - не трогай
    async def delete_aliase(message: types.Message):  # type: ignore
        id = message.from_user.id
        index = int(message.text.lower().split()[2])

        try:
            user_aliases = (await users.find_one({"id": id}))["aliases"]
            user_aliases.pop(index)
            await users.update_one({"id": id}, {"$set": {"aliases": user_aliases}})

            await message.reply("Алиас удалён")
        except Exception as e:
            debug(e)


    @_help(
        command = f"Алиасы",
        permissions = "all",
        description = "Показывает ваши алиасы или другого пользователя",
    )
    @dp.message_handler(lambda message: command(message, "алиасы", "all")) # Работает - не трогай
    async def user_aliases(message: types.Message):  # type: ignore
        try:
            if message.reply_to_message:
                id = message.reply_to_message.from_user.id
            else:
                id = message.from_user.id

            user_aliases = (await users.find_one({"id": id}))["aliases"]
            
            text = "*Алиасы*\n*> *`Индекс`: значение\n"
            for i, user_aliase in enumerate(user_aliases):
                text += f"`{i}`: {user_aliase}\n"

            await message.answer(text, parse_mode="Markdown")
        except:
            await message.answer("Нету алиасов")


class Utilities: # Работает - не трогай
    @classmethod
    def commands(cls):
        return [
            cls.alerts, cls.info  # type: ignore
        ]


    @_help(
        command = f"Воздушная тревога",
        description = "Список мест с воздушными тревогами в Украине.",
        permissions = "all"
    )
    @dp.message_handler(lambda message: command(message, "воздушная тревога", "all")) # Работает - не трогай
    async def alerts(message: types.Message):  # type: ignore
        try:
            alerts = await get_alerts()
            places = '\n'.join([alert + ' обл.' if alert.endswith('а') else alert for alert in alerts['alerts']])
            updated_at = alerts['updated_at']
            await message.answer(f"*Список мест с воздушной тревогой*:\n\n{places}\n\nОбновлено: `{updated_at}`", parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"*Ошибка!*\n```{e}```\n[FOUREX](tg://user?id={config['dev']})", parse_mode="Markdown")
    

    @_help(
        command = f"Инфо",
        description = "Ионормация о боте.",
        permissions = "all"
    )
    @dp.message_handler(lambda message: command(message, "инфо", "all")) # Работает - не трогай
    async def info(message: types.Message):  # type: ignore
        uptime = str(datetime.now() - start_time).split(".")[0]
        memory_usage = f"{virtual_memory().used // 1024 // 1024}/{virtual_memory().total // 1024 // 1024} МБ ({virtual_memory().percent}%)"
        cpu_load = f"{cpu_percent()}%"
        await message.answer(f"*Аптайм*: {uptime}\n*ОЗУ*: {memory_usage}\n*ЦПУ*: {cpu_load}\n[Разраб](tg://user?id={config['dev']})|[GitHub](https://github.com/FOUREX/brainfuck-on-top-utilities-bot)", parse_mode="Markdown")


@dp.message_handler(commands=["help"]) # Работает - не трогай
async def help(message: types.Message):  # type: ignore
    text = ""
    classes = {
        "Алиасы": Aliases.commands(),
        "Утилиты": Utilities.commands()
    }
    
    for cls in classes:
        text += f"\n*{cls}*\n"
        for command in classes[cls]:
            text += f"*>* `{command['command']} `"  # type: ignore

            if "args" in command:  # type: ignore
                for arg in command["args"]:  # type: ignore
                    text += "`{" + f"{arg}: {command['args'][arg]}" + "}` "  # type: ignore
            text += f"\n{command['description']} \n"  # type: ignore

    await message.answer(text, parse_mode="Markdown")


@dp.message_handler() # Работает - не трогай
async def aliase(message: types.Message):  # type: ignore
    for key in aliases:
        if key+"()" in message.text.lower().replace(" ", "").split():
            user = await bot.get_chat_member(chat_id, aliases[key])
            await message.reply(f"[{user.user.first_name}](tg://user?id={user.user.id})", parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=load_aliases)