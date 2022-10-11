from aiogram import Bot, Dispatcher
from datetime import datetime

from config import config


TOKEN = config["token"]


bot = Bot(TOKEN)
dp = Dispatcher(bot)

start_time = datetime.now()
