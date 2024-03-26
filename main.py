import asyncio
import logging
import sys

from aiogram import Dispatcher
from config import bot
from app.handlers import router

dp = Dispatcher()


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
