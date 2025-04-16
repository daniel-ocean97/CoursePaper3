import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from typing import List, Dict


class DBCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,

        )
        self.cursor = self.conn.cursor()
        # self.cursor.execute("""CREATE DATABASE vacancies""")


    def create_tables(self):
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

    def close(self):
        """Закрывает соединение с БД"""
        self.cursor.close()
        self.conn.close()