from os import listdir, mkdir, remove
from os.path import isdir
from datetime import datetime

from aiogram import executor, types
from importlib.util import spec_from_file_location, module_from_spec

from utilities.db import create_db, conn
from utilities.utilities import Logger
from bot import bot, dp
from config import config


PREFIX = config["prefix"]
LOG_IN_FILE = config["log_in_file"]


logger = Logger()
start_time = datetime.now()
loaded_cogs = {}


async def on_startup(*_):
    create_db()

    logger.info("Ready to fuck your mother (:")

    if LOG_IN_FILE:
        if not isdir("logs"):
            mkdir("logs")


async def on_shutdown(*_):
    conn.commit()
    conn.close()

    logger.info("Not ready to fuck your mother ):")
    logger.dump_log()
    remove("logs/latest")


def load_cogs():
    for cog in listdir("cogs"):
        if cog.endswith(".py"):
            spec = spec_from_file_location(cog, f"cogs/{cog}")
            lib = module_from_spec(spec)
            spec.loader.exec_module(lib)

            commands = lib.setup(bot, dp, logger)
            loaded_cogs.update(commands)


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    text = "*Команды бота*\n" \
          f"*~* _Префикс_ -> `{PREFIX}`" \
           "\n\n```" \
           "{аргумент} -> обязательный\n" \
           "[аргумент] -> не обязательный" \
           "\n```"

    for cog in loaded_cogs:
        text += f"\n\n*{cog}*"
        for command in loaded_cogs[cog]:
            text += f"\n*>* `{PREFIX + command.command}` "
            command_kwargs = command.command_kwargs

            if "args" in command_kwargs:
                args = command_kwargs["args"]
                for arg in args:
                    arg_type = args[arg]
                    if arg.endswith("*"):
                        if arg == "пользователь*":
                            arg = "{" + arg[:-1] + "}"
                        else:
                            arg = "{" + arg[:-1] + f": {arg_type}" + "}"
                    else:
                        if arg == "пользователь":
                            arg = f"[{arg}]"
                        else:
                            arg = f"[{arg}: {arg_type}]"

                    text += f"`{arg}` "

    await message.reply(text, parse_mode="Markdown")


def main():
    load_cogs()

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )


if __name__ == "__main__":
    main()
