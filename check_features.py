import asyncio

from sqlalchemy import text

from database import AsyncSessionLocal, close_database

from services.favorites import (
    add_favorite,
    get_favorites,
    remove_favorite,
)

from services.reports import add_report


# Тестовый пользователь. Позже заменим на реальный Telegram ID.
TEST_USER_ID = 123456789


async def main():
    try:
        # Получаем ID существующего пункта приёма
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("""
                SELECT id, address
                FROM points
                WHERE is_active = TRUE
                ORDER BY id
                LIMIT 1
            """))

            point = result.mappings().first()

        if point is None:
            print("В базе нет активных пунктов приёма.")
            return

        point_id = point["id"]

        print("Тестируем пункт:")
        print("ID:", point_id)
        print("Адрес:", point["address"])

        # 1. Добавление в избранное
        print("\n1. Добавление в избранное:")

        added = await add_favorite(TEST_USER_ID, point_id)

        if added:
            print("Пункт добавлен!")
        else:
            print("Пункт уже находился в избранном.")

        # 2. Просмотр избранного
        print("\n2. Список избранного:")

        favorites = await get_favorites(TEST_USER_ID)

        for number, favorite in enumerate(favorites, start=1):
            print(f"{number}. {favorite['address']}")
            print("Район:", favorite["district_name"])

        # 3. Создание жалобы
        print("\n3. Создание тестовой жалобы:")

        report_id = await add_report(
            telegram_user_id=TEST_USER_ID,
            point_id=point_id,
            report_type="wrong_address",
            comment="Тестовая жалоба для проверки программы."
        )

        print("Жалоба сохранена. ID:", report_id)

        # 4. Удаление из избранного
        print("\n4. Удаление из избранного:")

        removed = await remove_favorite(TEST_USER_ID, point_id)

        if removed:
            print("Пункт удалён из избранного.")
        else:
            print("Пункт не найден в избранном.")

        # 5. Повторная проверка
        favorites = await get_favorites(TEST_USER_ID)

        print("\nОсталось избранных пунктов:", len(favorites))

        print("\nВсе тесты завершены!")

    except Exception as error:
        print("\nПроизошла ошибка:")
        print(error)

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())