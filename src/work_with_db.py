import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from typing import List, Dict
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBCreator:
    def __init__(self, password: str, dbname: str = "vacancies"):
        self.dbname = dbname
        self.password = password
        self.__create_database()  # Создание БД с AUTOCOMMIT
        self.__connect()  # Обычное подключение
        self.__create_tables()  # Создание таблиц в транзакции


    def __create_database(self):
        # Подключение к postgres с AUTOCOMMIT
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=self.password,
            host="localhost"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {self.dbname}")
        finally:
            cursor.close()
            conn.close()

    def __connect(self):
        # Обычное подключение к целевой БД
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user="postgres",
            password=self.password,
            host="localhost"
        )
        self.cursor = self.conn.cursor()


    def __create_tables(self):
        """Создает таблицы в БД"""
        self.cursor.execute("""
            DROP TABLE IF EXISTS vacancies CASCADE;
            DROP TABLE IF EXISTS employers CASCADE;
            
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE);

            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(id),
                title TEXT NOT NULL,
                salary_min INTEGER,
                salary_max INTEGER,
                url TEXT NOT NULL);
        """)
        self.conn.commit()

    def insert_employers(self, employers: List[str]):
        """Добавляет компании в БД"""
        query = sql.SQL("INSERT INTO employers (name) VALUES (%s) ")
        execute_batch(self.cursor, query, [(e,) for e in employers])
        self.conn.commit()

    def insert_vacancies(self, vacancies: List[Dict]):
        """Добавляет вакансии в БД"""
        self.cursor.execute("SELECT id, name FROM employers")
        employer_ids = {row[1]: row[0] for row in self.cursor.fetchall()}

        query = """
            INSERT INTO vacancies (employer_id, title, salary_min, salary_max, url)
            VALUES (%s, %s, %s, %s, %s)   
        """
        data = []
        for v in vacancies:
            employer_name = v.get('employer')
            employer_id = employer_ids.get(employer_name)

            if not employer_id:
                continue  # Пропускаем вакансии с неизвестным работодателем

            data.append((
                employer_id,
                v.get('title'),
                v.get('salary_min'),
                v.get('salary_max'),
                v.get('url')
            ),)

        # 4. Пакетная вставка
        if data:
            execute_batch(self.cursor, query, data)
            self.conn.commit()

    def close(self) -> None:
        """Закрывает соединение с БД"""
        self.cursor.close()
        self.conn.close()

    def drop_database(self) -> None:
        """Удаляет базу данных"""
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="3228",
            host="localhost"
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = self.conn.cursor()

        cursor.execute(f"DROP DATABASE {self.dbname}")



class DBManager:
    def __init__(self, password: str, dbname: str = "vacancies"):
        self.dbname = dbname
        self.password = password
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user="postgres",
            password=self.password,
            host="localhost"
        )
        self.cursor = self.conn.cursor()

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        self.cursor.execute("""
                SELECT 
                    e.name AS company_name,
                    COUNT(v.id) AS vacancies_count
                FROM 
                    employers e
                LEFT JOIN 
                    vacancies v ON e.id = v.employer_id
                GROUP BY 
                    e.name
                ORDER BY 
                    vacancies_count DESC;
            """)
        result = self.cursor.fetchall()
        return result

    def get_all_vacancies(self):
        """Получает все вакансии"""
        self.cursor.execute("""
        SELECT 
            e.name AS company_name,
            v.title,
            v.salary_min,
            v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id""")
        result = self.cursor.fetchall()
        return result

    def get_avg_salary(self):
        """Получает среднюю зарплату"""
        self.cursor.execute("""
        SELECT ROUND(AVG((v.salary_min+v.salary_max)/2)) as avg_salary
            FROM vacancies v
            WHERE salary_min IS NOT NULL 
            OR salary_max IS NOT NULL""")
        result = self.cursor.fetchall()
        return int(result[0][0])

    def get_vacancies_with_higher_salary(self):
        """Получает вакансии с зарплатой выше средней"""
        self.cursor.execute(f"""
        SELECT title, url 
        FROM vacancies v
        WHERE (v.salary_min+v.salary_max)/2 > {self.get_avg_salary()} """)
        result = self.cursor.fetchall()
        return result

    def vacancies_with_keyword(self, keyword: str):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        self.cursor.execute(f"""
        SELECT title,salary_min, salary_max, url
        FROM vacancies
        WHERE title LIKE '%{keyword}%'""")
        result = self.cursor.fetchall()
        return result


