
import asyncio

from sqlalchemy import text, bindparam
from database import AsyncSessionLocal, close_database


SAFE_CATEGORIES = (
    "Пластик",
    "Бумага",
    "Металл",
    "Стекло",
    "Одежда",
    "Батарейки",
    "Лампочки",
    "Крышечки",
    "Зубные щётки",
)


async def audit_database():
    try:
        async with AsyncSessionLocal() as session:

            # 1. Общая статистика
            print("\n========== 1. ОБЩАЯ СТАТИСТИКА ==========\n")

            result = await session.execute(text("""
                SELECT
                    (SELECT COUNT(*) FROM districts) AS districts,
                    (SELECT COUNT(*) FROM categories) AS categories,
                    (SELECT COUNT(*) FROM points) AS total_points,
                    (SELECT COUNT(*) FROM points WHERE is_active = TRUE) AS active_points,
                    (SELECT COUNT(*) FROM points WHERE is_active = FALSE) AS inactive_points,
                    (SELECT COUNT(*) FROM point_categories) AS category_links
            """))

            stats = result.mappings().one()

            for name, value in stats.items():
                print(f"{name}: {value}")

            # 2. Покрытие районов и категорий
            print("\n========== 2. ПОКРЫТИЕ 15 РАЙОНОВ × 9 КАТЕГОРИЙ ==========\n")

            coverage_query = text("""
                SELECT
                    d.name AS district,
                    c.name AS category,
                    COUNT(DISTINCT pc.point_id) AS point_count
                FROM districts d
                CROSS JOIN categories c
                LEFT JOIN points p
                    ON p.district_id = d.id
                   AND p.is_active = TRUE
                LEFT JOIN point_categories pc
                    ON pc.point_id = p.id
                   AND pc.category_id = c.id
                WHERE c.name IN :category_names
                GROUP BY d.id, d.name, c.id, c.name
                ORDER BY d.name, c.name
            """).bindparams(
                bindparam("category_names", expanding=True)
            )

            result = await session.execute(
                coverage_query,
                {"category_names": SAFE_CATEGORIES}
            )

            coverage = result.mappings().all()

            missing = []
            underfilled = []

            for row in coverage:
                count = row["point_count"]

                if count == 0:
                    missing.append(row)
                elif count < 4:
                    underfilled.append(row)

                print(
                    f'{row["district"]:<22} | '
                    f'{row["category"]:<20} | '
                    f'{count} адресов'
                )

            # 3. Отсутствующие категории
            print("\n========== 3. ОТСУТСТВУЮЩИЕ КАТЕГОРИИ ==========\n")

            if missing:
                for row in missing:
                    print(f'{row["district"]}: {row["category"]}')
            else:
                print("Отсутствующих категорий нет.")

            # 4. Менее четырёх адресов
            print("\n========== 4. МЕНЬШЕ ЧЕТЫРЁХ АДРЕСОВ ==========\n")

            if underfilled:
                for row in underfilled:
                    print(
                        f'{row["district"]}: '
                        f'{row["category"]} — '
                        f'{row["point_count"]} адресов'
                    )
            else:
                print("Все сочетания имеют минимум 4 адреса.")

            # 5. Повторяющиеся адреса
            print("\n========== 5. ПОВТОРЯЮЩИЕСЯ АДРЕСА ==========\n")

            duplicate_query = text("""
                SELECT
                    LOWER(TRIM(address)) AS normalized_address,
                    district_id,
                    COUNT(*) AS duplicate_count,
                    STRING_AGG(id::TEXT, ', ') AS point_ids
                FROM points
                WHERE is_active = TRUE
                GROUP BY LOWER(TRIM(address)), district_id
                HAVING COUNT(*) > 1
                ORDER BY duplicate_count DESC
            """)

            result = await session.execute(duplicate_query)
            duplicates = result.mappings().all()

            if duplicates:
                for row in duplicates:
                    print(
                        f'{row["normalized_address"]} | '
                        f'ID: {row["point_ids"]} | '
                        f'Повторов: {row["duplicate_count"]}'
                    )
            else:
                print("Дубликатов по точному адресу в одном районе нет.")

            # 6. Пункты без категорий
            print("\n========== 6. ПУНКТЫ БЕЗ КАТЕГОРИЙ ==========\n")

            result = await session.execute(text("""
                SELECT p.id, p.address
                FROM points p
                LEFT JOIN point_categories pc
                    ON pc.point_id = p.id
                WHERE p.is_active = TRUE
                  AND pc.point_id IS NULL
            """))

            points_without_categories = result.mappings().all()

            if points_without_categories:
                for point in points_without_categories:
                    print(f'ID {point["id"]}: {point["address"]}')
            else:
                print("Пунктов без категорий нет.")

            print("\n========== АУДИТ ЗАВЕРШЁН ==========\n")

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(audit_database())
