from src.external_api import HHAPI
from src.work_with_db import DBCreator, DBManager
from config import companies

def main():
    # 1. Загрузка данных
    hh = HHAPI()
    vacancies, employers = hh.load_vacancies(companies)


    # 2. Инициализация БД
    db = DBCreator(dbname="hh_vacancies", password="3228")

    try:
        db.insert_employers(employers)
        db.insert_vacancies(vacancies)
    finally:
        db.close()


if __name__ == "__main__":
    #main()
    db = DBManager(dbname="hh_vacancies", password="3228")
    print(db.get_companies_and_vacancies_count())
    #print(db.get_all_vacancies())
    print(db.get_avg_salary())
    print(db.get_vacancies_with_higher_salary())
    print(db.vacancies_with_keyword('Python'))