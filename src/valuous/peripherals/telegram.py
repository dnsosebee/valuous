from teleapi.httpx_transport import httpx_teleapi_factory
from teleapi.teleapi import Teleapi

from valuous.settings import settings


def get_bot():
    telegram_bot_token = settings.telegram_bot_token
    return httpx_teleapi_factory(telegram_bot_token, timeout=10)


def get_updates(bot: Teleapi):
    updates = bot.get
    return updates
