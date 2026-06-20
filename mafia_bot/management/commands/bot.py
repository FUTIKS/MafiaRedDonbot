import asyncio
import logging
import sys
from django.core.management import BaseCommand

from mafia_bot.handlers import *
from mafia_bot.utils import set_bot_commands
from mafia_bot import redis_state
from dispatcher import dp, bot


async def main() -> None:
    await set_bot_commands(bot)
    await redis_state.rehydrate_all()                  # restore mirrored state
    asyncio.create_task(redis_state.snapshot_loop())   # keep mirroring it
    await dp.start_polling(bot)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())