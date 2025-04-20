import os

from dotenv import load_dotenv

from config import companies
from src.external_api import HHAPI
from src.work_with_db import DBCreator, DBManager

load_dotenv()  # Загрузка переменных окружения из .env


def main():
    print("Здравствуй! Начинаю загрузку данных по следующим компаниям:")
    for i in range(len(companies)):
        print(f"{i+1}. {companies[i]}")
    # 1. Загрузка данных
    hh = HHAPI()
    vacancies, employers = hh.load_vacancies(companies)
    dbname = os.getenv("DB_NAME")
    password = os.getenv("DB_PASSWORD")
    # 2. Инициализация БД
    vacancies_db = DBCreator(dbname=dbname, password=password)
    db_manager = DBManager(dbname=dbname, password=password)

    try:
        req = ""
        print("Данные загружены!")
        vacancies_db.insert_employers(employers)
        vacancies_db.insert_vacancies(vacancies)
        while req != "0":
            req = input(
                """Выбери действие из списка (указать цифру без точки)
            1. Получить список всех компаний и количество вакансий у каждой компании
            2. Получить все вакансии
            3. Получить среднюю зарплату
            4. Получить вакансии с зарплатой выше средней
            5. Получить список всех вакансий, по ключевому слову в названии
            6. Удалить Базу Данных
            0. Выход из программы\n"""
            )
            if req == "1":
                for company in db_manager.get_companies_and_vacancies_count():
                    print(company)
            elif req == "2":
                for vacancy in db_manager.get_all_vacancies():
                    print(vacancy)
            elif req == "3":
                print(f"Средняя зарплата - {db_manager.get_avg_salary()}")
            elif req == "4":
                for vacancy in db_manager.get_vacancies_with_higher_salary():
                    print(vacancy)
            elif req == "5":
                keyword = input("Введите ключевое слово\n")
                for vacancy in db_manager.vacancies_with_keyword(keyword):
                    print(vacancy)
            elif req == "6":
                db_manager.close()
                vacancies_db.close()
                vacancies_db.drop_database()
            elif req == "0":
                print("До свидания!")
                pass
    finally:
        db_manager.close()
        vacancies_db.close()


if __name__ == "__main__":
    main()
