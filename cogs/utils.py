from os import listdir
from datetime import datetime

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.bot.bot import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from psutil import cpu_percent, virtual_memory, disk_usage

from bot import start_time
from utilities.utilities import message_command, command_check, Logger
from utilities.alerts import get_alerts_map, get_alerts, get_alerts_map_theme, set_alerts_map_theme
from config import config


custom_data = CallbackData("post", "action", "data")


def select_theme_buttons(selected_theme: str):
    themes = listdir("src/alerts/themes")
    themes.sort()
    buttons = []

    for theme in themes:
        if theme == str(selected_theme):
            theme = f"✅ {theme}"
        button = InlineKeyboardButton(text=theme, callback_data=custom_data.new(action="set theme", data=theme))
        buttons.append(button)

    return buttons


class Utils:
    def __init__(self, bot: Bot, logger: Logger):
        self.bot = bot
        self.logger = logger

    @classmethod
    def commands(cls) -> dict:
        return {
            "Утилиты": [cls.alerts, cls.bot_info]
        }

    @message_command(
        command="тревога",
        description="Показывает места с воздушной тревогой в Украине."
    )
    async def alerts(self, message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        alerts_map = get_alerts_map(chat_id, user_id)
        alerts = get_alerts()
        alerts_locates = alerts["locates"]

        button = InlineKeyboardButton(
            text="Сменить тему",
            callback_data=custom_data.new(action="change theme", data="")
        )

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(button)

        text = ""

        oblasts = {}
        hromades = {}
        cities = {}

        for locate in alerts_locates:
            locate_info = alerts_locates[locate]

            match locate_info["type"]:
                case "oblast":
                    oblasts.update({locate: locate_info})
                case "hromada":
                    hromades.update({locate: locate_info})
                case "city":
                    cities.update({locate: locate_info})

        for locates in [oblasts, hromades, cities]:
            if locates:
                for locate in locates:
                    text += locate + "\n"

                text += "\n"

        await message.reply_photo(alerts_map, caption=text, reply_markup=markup)

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

        msg = "*Статистика*\n" \
              "\n" \
              f"*ОЗУ*: {ram_used}/{ram_total} МБ ({ram_used_percent:.1f}%)\n" \
              f"*ЦПУ*: {cpu_percent()}%\n" \
              f"*Диск*: {disk_used}/{disk_total} ГБ ({disk_used_percent:.1f}%)\n" \
              f"*Аптайм*: {uptime}\n" \
              "\n" \
              "\n" \
              "*Информация*\n" \
              "\n" \
              f"[Разработчик](tg://user?id={config['dev_id']})|" \
              f"[GitHub](https://github.com/FOUREX/brainfuck-on-top-utilities-bot)"

        await message.answer(msg, parse_mode="Markdown")

    @staticmethod
    async def change_alerts_map_theme(call: CallbackQuery):
        chat_id = call.message.chat.id
        user_id = call.from_user.id

        markup = InlineKeyboardMarkup(row_width=5)

        selected_theme = get_alerts_map_theme(chat_id, user_id)

        buttons = select_theme_buttons(selected_theme)
        markup.add(*buttons)

        await call.message.edit_reply_markup(markup)

    @staticmethod
    async def set_alerts_map_theme(call: CallbackQuery, callback_data: dict):
        chat_id = call.message.chat.id
        user_id = call.from_user.id

        selected_theme = get_alerts_map_theme(chat_id, user_id)

        theme_to_set = callback_data["data"].split()[-1]
        markup = InlineKeyboardMarkup(row_width=5)

        if theme_to_set == selected_theme:
            await call.answer("Эта тема уже выбрана!")

        selected_theme = theme_to_set
        set_alerts_map_theme(chat_id, user_id, selected_theme)

        buttons = select_theme_buttons(selected_theme)
        markup.add(*buttons)

        await call.message.edit_reply_markup(markup)


def setup(bot: Bot, dp: Dispatcher, logger: Logger) -> dict:
    utils = Utils(bot, logger)

    _alerts = utils.alerts
    _bot_info = utils.bot_info

    dp.register_message_handler(_alerts, lambda message: command_check(message, _alerts.command))
    dp.register_message_handler(_bot_info, lambda message: command_check(message, _bot_info.command))

    _change_alerts_map_theme = utils.change_alerts_map_theme
    _set_alerts_map_theme = utils.set_alerts_map_theme

    dp.register_callback_query_handler(_change_alerts_map_theme, custom_data.filter(action=["change theme"]))
    dp.register_callback_query_handler(_set_alerts_map_theme, custom_data.filter(action=["set theme"]))

    return utils.commands()
