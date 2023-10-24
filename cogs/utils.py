from os import listdir
from datetime import datetime

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.bot.bot import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from psutil import cpu_percent, virtual_memory, disk_usage

from bot import alerts_client, start_time
from utilities.utilities import message_command, command_check, get_user, Logger
from config import config


class Utils:
    def __init__(self, bot: Bot, logger: Logger):
        self.bot = bot
        self.logger = logger

    @classmethod
    def commands(cls) -> dict:
        return {
            "Утилиты": [cls.alerts, cls.user_info, cls.bot_info]
        }

    @message_command(
        command="тревога",
        aliases=("тривога", "тр", "alerts", "al"),
        description="Карта воздушных тревог в Украине."
    )
    async def alerts(self, message: Message):
        locations = await alerts_client.get_active()
        alerts_map = locations.render_map()

        cities = "\n".join(locations.filter(location_type="city").location_title)
        hromades = "\n".join(locations.filter(location_type="hromada").location_title)
        oblasts = "\n".join(locations.filter(location_type="oblast").location_title)

        text = f"{oblasts}\n\n{hromades}\n\n{cities}"

        await message.reply_photo(alerts_map, text)

    @message_command(
        command="инфо",
        description="Информация о пользователе"
    )
    async def user_info(self, message: Message):
        user = get_user(message)

        message_text = f"*Информация о {user.mention}*" \
                       f"" \
                       f"" \
                       f"" \
                       f"" \
                       f""

        await message.reply(message_text, parse_mode="Markdown")

    @message_command(
        command="бот",
        description="Информация о сервере и боте."
    )
    async def bot_info(self, message: Message):
        uptime = str(datetime.now() - start_time).split(".")[0]
        ram_total = virtual_memory().total // 1024 // 1024
        ram_used = virtual_memory().used // 1024 // 1024
        ram_used_percent = virtual_memory().percent
        disk_total = disk_usage('/').total // 1024 // 1024 // 1024
        disk_used = disk_usage('/').used // 1024 // 1024 // 1024
        disk_used_percent = disk_usage('/').percent

        msg = "*Статистика*\n\n" \
              f"*ОЗУ*: {ram_used}/{ram_total} МБ ({ram_used_percent:.1f}%)\n" \
              f"*ЦПУ*: {cpu_percent()}%\n" \
              f"*Диск*: {disk_used}/{disk_total} ГБ ({disk_used_percent:.1f}%)\n" \
              f"*Аптайм*: {uptime}\n\n\n" \
              f"*Информация*\n\n" \
              f"[Разработчик](tg://user?id={config['dev_id']})|" \
              f"[GitHub](https://github.com/FOUREX/brainfuck-on-top-utilities-bot)"

        await message.answer(msg, parse_mode="Markdown")


def setup(bot: Bot, dp: Dispatcher, logger: Logger) -> dict:
    utils = Utils(bot, logger)

    _alerts = utils.alerts
    _user_info = utils.user_info
    _bot_info = utils.bot_info

    dp.register_message_handler(_alerts, lambda message: command_check(message, _alerts.command, True, _alerts.aliases))
    dp.register_message_handler(_user_info, lambda message: command_check(message, _user_info.command, True))
    dp.register_message_handler(_bot_info, lambda message: command_check(message, _bot_info.command, True))

    return utils.commands()
