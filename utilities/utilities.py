from aiogram.types import Message, User
from datetime import datetime
from termcolor import colored

from bot import start_time
from config import config


PREFIX = config["prefix"]
BOT_NAME = config["name"]
ALLOWED_CHAT_ID = config["allowed_chat_id"]
LOG_IN_FILE = config["log_in_file"]


def get_time():
    time = datetime.now().strftime("%H:%M")
    return time


def get_date():
    date = datetime.now().strftime("%m.%d")
    return date


def get_user(message: Message) -> User:
    """
    Возвращает пользователя на чьё сообщение ответили, в ином случае автора сообщения
    """

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    return user


def get_user_id(message: Message) -> int:
    """
    Возвращает id пользователя на чьё сообщение ответили, в ином случае id автора сообщения
    """

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.from_user.id

    return user_id


def get_args(message_text: str, command: str, to_lower: bool = False, _type=str, max_length: int = 32) -> list | None:
    command_length = len(PREFIX) + len(command)
    message_text = message_text[command_length:]
    message_text = message_text.lower() if to_lower else message_text

    args = message_text.split()

    if args:
        args = [_type(arg[:max_length]) for arg in args]
    else:
        return None

    return args


def message_command(**kwargs):
    def wrapper(function):
        function.command_kwargs = kwargs
        function.command = kwargs["command"]
        function.aliases = []
        function.args = {}

        if "aliases" in kwargs:
            function.aliases = kwargs["aliases"]

        if "args" in kwargs:
            function.args = kwargs["args"]

        return function

    return wrapper


def command_check(message: Message, command: str, public: bool = False, aliases: list | tuple = None):
    if message.chat.id != ALLOWED_CHAT_ID and not public:
        return False

    command = PREFIX + command
    _message_command = message.text.lower()[:len(command)]

    check = _message_command == command

    if not check and aliases:
        for alias in aliases:
            command = PREFIX + alias
            _message_command = message.text.lower()[:len(command)]

            check = _message_command == command

            if check:
                break

    return check


class Logger:
    @staticmethod
    def dump_log():
        _start_time = start_time.strftime('%m-%d %H.%M')
        _end_time = datetime.now().strftime('%m-%d %H.%M')
        name = f"{_start_time} - {_end_time}"
        with open(f"logs/{name}", "w") as f:
            with open("logs/latest", "r") as _f:
                log = _f.read()
                _f.close()

            f.write(log)

    @staticmethod
    def log_in_file(message):
        if not LOG_IN_FILE:
            return

        message = f"{message}\n"
        with open("logs/latest", "a", encoding="utf-8") as f:
            f.write(message)

            f.close()

    def info(self, message):
        time_now = get_time()
        date_now = get_date()

        message = f"🗸[{date_now} | {time_now}] {BOT_NAME}: {message}"

        print(colored(message, "blue"))

        self.log_in_file(message)

    def warn(self, message):
        time_now = get_time()
        date_now = get_date()

        message = f"![{date_now} | {time_now}] {BOT_NAME}: {message}"

        print(colored(message, "yellow"))

        self.log_in_file(message)

    def error(self, message):
        time_now = get_time()
        date_now = get_date()

        message = f"✗[{date_now} | {time_now}] {BOT_NAME}: {message}"

        print(colored(message, "red"))

        self.log_in_file(message)
