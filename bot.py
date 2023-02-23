from os import environ
from datetime import datetime

from alerts_in_ua.async_alerts_client import AsyncAlertsClient
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


load_dotenv()

ALERTS_TOKEN = environ.get("alerts_token")
BOT_TOKEN = environ.get("bot_token")

alerts_client = AsyncAlertsClient(ALERTS_TOKEN)
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

start_time = datetime.now()
