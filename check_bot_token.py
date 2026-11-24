import asyncio

from aiogram import Bot
from config import settings


async def main():
    if not settings.bot_token:
        print("Ошибка: токен не найден в файле .env")
        return

    bot = Bot(token=settings.bot_token)

    try:
        print("Проверяем токен...")

        bot_info = await bot.get_me()

        print("\nТокен действителен!")
        print("Название бота:", bot_info.full_name)
        print("Username:", f"@{bot_info.username}")
        print("ID бота:", bot_info.id)

    except Exception as error:
        print("\nНе удалось проверить токен.")
        print("Тип ошибки:", type(error).__name__)
        print("Описание:", error)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())