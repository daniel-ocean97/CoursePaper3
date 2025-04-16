from src.external_api import HHAPI
from src.create_db import DBCreator
from config import companies

def main():
    # 1. Загрузка данных
    hh = HHAPI()
    vacancies, employers = hh.load_vacancies(companies)


    # 2. Инициализация БД
    db = DBCreator(
        dbname="vacancies",
        user="postgres",
        password="3228"
    )

    try:
        db.create_tables()
        db.insert_employers(employers)
        db.insert_vacancies(vacancies)
    finally:
        db.close()


if __name__ == "__main__":
    main()