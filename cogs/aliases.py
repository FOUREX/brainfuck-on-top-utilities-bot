import sqlite3

from aiogram.types import Message
from aiogram.bot.bot import Bot
from aiogram.dispatcher.dispatcher import Dispatcher

from utilities.db import cur, conn
from utilities.utilities import message_command, command_check, get_args, get_user, Logger
from config import config


DEV_ID = config["dev_id"]

LIMIT_ALIASES = 50
LIMIT_ALIAS_LENGTH = 32


class Aliases:
    def __init__(self, bot: Bot, logger: Logger):
        self.bot = bot
        self.logger = logger

    @classmethod
    def commands(cls) -> dict:
        return {
            "Алиасы": [cls.new_alias, cls.aliases, cls.delete_alias, cls.purge_aliases]
        }

    @message_command(
        command="новый алиас",
        args={"пользователь*": "ответ на сообщение", "алиас*": "*str"},
        usage="!Новый алиас толик \n!Новый алиас толик шайба карбюратор",
        description="Алиасы добавятся для того пользователя на чьё сообщение Вы ответили.",
        note=f"Максимальное количество алиасов: `{LIMIT_ALIASES}`"
             f"Максимальная длинна алиаса: `{LIMIT_ALIAS_LENGTH}` символа"
    )
    async def new_alias(self, message: Message):
        chat_id = message.chat.id
        user = get_user(message)
        user_id = user.id
        aliases = get_args(message.text, self.new_alias.command, True, max_length=LIMIT_ALIAS_LENGTH)

        if aliases:
            data = [(chat_id, arg, user_id) for arg in aliases]
        else:
            await message.reply("🟡 Пропущен аргумент \"алиас\"")
            return

        try:
            cur.execute(f"SELECT COUNT(*) FROM aliases WHERE chat_id = ? and user_id = ?", (chat_id, user_id))
            count_aliases = cur.fetchone()[0]
            slots = LIMIT_ALIASES - count_aliases
            aliases = aliases[:slots]
            data = data[:slots]

            if slots > 0:
                cur.executemany("INSERT INTO aliases VALUES (?, ?, ?)", data)

                text = f"🟢 *Алиасы добавлены для {user.mention}*\n" \
                       f"> `Индекс`: значение\n\n"
                text += "\n".join(f'`{index}`: {alias}' for index, alias in enumerate(aliases))

                await message.reply(text, parse_mode="Markdown")

            else:
                await message.reply(f"🔴 Вы достигли лимита `{LIMIT_ALIASES}` алиасов!", parse_mode="Markdown")

        except sqlite3.IntegrityError as error:
            match str(error):
                case "UNIQUE constraint failed: aliases.alias":
                    await message.reply("🔴 Один или несколько из указанных алиасов заняты другими пользователями!")
                case _:
                    await message.reply("🔴 Неизвестная ошибка! Попробуйте снова.")
                    self.logger.error(error)

        conn.commit()

    @message_command(
        command="алиасы",
        args={"пользователь": "ответ на сообщение"},
        description="Показывает ваши или другого пользователя алиасы."
    )
    async def aliases(self, message: Message):
        chat_id = message.chat.id
        user = get_user(message)
        user_id = user.id

        cur.execute("SELECT alias FROM aliases WHERE chat_id = ? and user_id = ?", (chat_id, user_id))
        aliases = cur.fetchmany(LIMIT_ALIASES)

        text = f"*Алиасы {user.mention}*\n" \
               f"> `Индекс`: значение\n\n"

        text += "\n".join([f"{index}: {alias[0]}" for index, alias in enumerate(aliases)])

        print(text[::len(text)])

        await message.reply("Алиасов не будет, разработчик закончил жизнь самоубийством", parse_mode="Markdown")
        # await message.reply(text[::len(text)], parse_mode="Markdown")

    @message_command(
        command="удалить алиас",
        args={"индекс*": "*int"},
        description="Удаляет алиас по индексу. Индексы алиасов можно узнать командой `!Алиасы`."
    )
    async def delete_alias(self, message: Message):
        chat_id = message.chat.id
        user = message.from_user
        user_id = user.id

        if user_id == DEV_ID:
            user = get_user(message)
            user_id = user.id

        try:
            args = get_args(message.text, self.delete_alias.command, _type=int)
        except ValueError:
            await message.reply("🔴 Неверно введены аргументы!")
            return

        if args is None:
            await message.reply("🟡 Пропущен аргумент \"индекс\"")
            return

        cur.execute("SELECT alias FROM aliases WHERE chat_id = ? and user_id = ?", (chat_id, user_id))
        aliases = cur.fetchmany(LIMIT_ALIASES)

        text = f"🟢 *Алиасы удалены для {user.mention}*\n" \
               f"> `Индекс`: значение\n\n"
        to_delete = []

        for index in args:
            index = abs(index)
            if 0 <= index <= len(aliases) - 1:
                alias = aliases[index][0]

                if (chat_id, alias) in to_delete:
                    continue

                text += f"`{index}`: {alias}\n"
                to_delete.append((chat_id, alias))

        cur.executemany("DELETE FROM aliases WHERE chat_id = ? and alias = ?", to_delete)

        await message.reply(text, parse_mode="Markdown")
        conn.commit()

    @message_command(
        command="очистить алиасы",
        description="Удаляет все алиасы."
    )
    async def purge_aliases(self, message: Message):
        chat_id = message.chat.id
        user = message.from_user

        if user.id == DEV_ID:
            if message.reply_to_message:
                user = message.reply_to_message.from_user

        user_id = user.id

        cur.execute("DELETE FROM aliases WHERE chat_id = ? and user_id = ?", (chat_id, user_id))

        await message.reply(f"🟢 *Алиасы очищены для {user.mention}*", parse_mode="Markdown")
        conn.commit()

    @staticmethod
    async def detect_alias(message: Message):
        chat_id = message.chat.id
        message_text = message.text.lower()

        offset = message_text.find("()")
        alias = message_text[:offset]
        alias = alias.replace(" ", "")

        sql = "SELECT user_id FROM aliases WHERE chat_id = ? AND alias = ?"
        cur.execute(f"SELECT EXISTS ({sql})", (chat_id, alias))
        alias_is_exists = bool(cur.fetchone()[0])

        if not alias_is_exists:
            return

        cur.execute(sql, (chat_id, alias))
        user_id = cur.fetchone()[0]

        await message.reply(f"[{alias.title()}](tg://user?id={user_id})", parse_mode="Markdown")


def setup(bot: Bot, dp: Dispatcher, logger: Logger) -> dict:
    aliases = Aliases(bot, logger)

    _new_alias = aliases.new_alias
    _aliases = aliases.aliases
    _delete_alias = aliases.delete_alias
    _purge_alias = aliases.purge_aliases
    _detect_alias = aliases.detect_alias

    dp.register_message_handler(_new_alias, lambda message: command_check(message, _new_alias.command, True))
    dp.register_message_handler(_aliases, lambda message: command_check(message, _aliases.command, True))
    dp.register_message_handler(_delete_alias, lambda message: command_check(message, _delete_alias.command, True))
    dp.register_message_handler(_purge_alias, lambda message: command_check(message, _purge_alias.command, True))
    dp.register_message_handler(_detect_alias, lambda message: "()" in message.text)

    return aliases.commands()
