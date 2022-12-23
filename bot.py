from os import environ
from datetime import datetime

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


load_dotenv()


TOKEN = environ.get("token")


bot = Bot(TOKEN)
dp = Dispatcher(bot)

start_time = datetime.now()
