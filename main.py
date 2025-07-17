import asyncio

from aiogram.client.default import DefaultBotProperties
from loguru import logger

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from config import BOT_TOKEN
from database.db import engine
from database.models import Base
from handlers import instruction, payment, admin, common
from scheduler.tasks import cleanup_expired_users, delete_empty_servers

print("Creating tables...")
Base.metadata.create_all(bind=engine)

logger.add("logs/bot.log", rotation="10 MB", compression="zip")


async def start_bot():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Please set it in config.py or environment variables.")
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))  # ✅ корректно для Aiogram 3.4+
    dp = Dispatcher()
    dp.fsm.strategy = FSMStrategy.CHAT

    dp.include_router(common.router)
    dp.include_router(instruction.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)


async def start_webhook():
    config = uvicorn.Config(
        "webhook.payment_webhook:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main_async():
    await asyncio.gather(
        start_bot(),
        start_webhook()
    )


def main():
    # ⛔ Эти функции синхронные — вызываем ДО async
    cleanup_expired_users()
    delete_empty_servers()

    # 🚀 Запускаем асинхронные процессы
    asyncio.run(main_async())


if __name__ == "__main__":
    main()