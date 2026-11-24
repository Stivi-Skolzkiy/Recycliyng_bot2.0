
import asyncio

from services.catalog import (
    get_categories,
    get_districts,
    get_points_by_category_and_district,
)
from database import close_database


async def main():
    try:
        # Получаем категории и районы
        categories = await get_categories()
        districts = await get_districts()

        # Выбираем категорию «Пластик»
        category = next(
            (item for item in categories if item["name"] == "Пластик"),
            None
        )

        # Выбираем район «Алексеевский»
        district = next(
            (item for item in districts if item["name"] == "Алексеевский"),
            None
        )

        if category is None:
            print("Категория «Пластик» не найдена.")
            return

        if district is None:
            print("Район «Алексеевский» не найден.")
            return

        print("Поиск пунктов приёма...")
        print("Категория:", category["name"])
        print("Район:", district["name"])
        print("-" * 45)

        # Ищем адреса
        points = await get_points_by_category_and_district(
            category_id=category["id"],
            district_id=district["id"]
        )

        if not points:
            print("В этом районе пока нет найденных пунктов.")
            return

        for number, point in enumerate(points, start=1):
            print(f"\n{number}. {point['name'] or 'Пункт приёма'}")
            print("Адрес:", point["address"])
            print("Принимают:", point["accepted_categories"])

        print("\nВсего найдено пунктов:", len(points))

    except Exception as error:
        print("\nПроизошла ошибка:")
        print(error)

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
