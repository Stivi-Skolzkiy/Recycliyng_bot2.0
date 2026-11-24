
import asyncio

from database import check_database_connection, close_database


async def main():
    try:
        print("Подключаемся к PostgreSQL...")

        data = await check_database_connection()

        print("\nПодключение успешно!")
        print("Версия PostgreSQL:", data["version"])

        print("\nСтатистика базы данных:")
        print("Районов:", data["districts"])
        print("Категорий:", data["categories"])
        print("Пунктов приёма:", data["points"])
        print("Связей пунктов с категориями:", data["point_categories"])

    except Exception as error:
        print("\nНе удалось подключиться к базе данных.")
        print("Ошибка:", error)

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
