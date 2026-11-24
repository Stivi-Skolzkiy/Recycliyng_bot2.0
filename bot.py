
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config import settings
from database import close_database
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router
from handlers.favorites import router as favorites_router
from handlers.reports import router as reports_router


async def main():
    if not settings.bot_token:
        raise ValueError("Не указан токен Telegram-бота в файле .env")

    # Используем локальный прокси
    session = AiohttpSession(proxy="http://127.0.0.1:10809")

    bot = Bot(
        token=settings.bot_token,
        session=session
    )

    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(catalog_router)
    dp.include_router(favorites_router)
    dp.include_router(reports_router)

    print("ЭкоПомощник СВАО запускается...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
