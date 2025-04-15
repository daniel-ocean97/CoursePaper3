from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class JobAPI(ABC):
    """Абстрактный класс для работы с API вакансий"""

    @abstractmethod
    def connect(self) -> None:
        """Метод для установки соединения с API"""
        pass

    @abstractmethod
    def load_vacancies(
        self, keyword: str, *args: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """Метод для получения вакансий по ключевому слову"""
        pass


class HHAPI(JobAPI):
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self):
        self.__url = "https://api.hh.ru/"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.__params = {"text": "", "page": 0, "per_page": 100}
        self.__vacancies = []
        self.__connected = False
        self.__session = requests.Session()

    def connect(self):
        """Публичный метод для реализации абстрактного класса"""
        self.__establish_connection()

    def __establish_connection(self):
        """Приватный метод для реального подключения"""
        try:
            response = self.__session.get(f"{self.__url}", headers=self.__headers)
            response.raise_for_status()
            self.__connected = True
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка подключения: {e}")

    def __get_employer_ids(self, company) -> List[str]:
        """Получает ID работодателей по их названиям"""
        id = ""
        response = self.__session.get(
            f"{self.__url}employers",
            params={'text': company, 'only_with_vacancies': True},
            headers=self.__headers
        )
        items = response.json().get('items', [])
        if items:
            id = items[0]['id']
        print(company, items[0]['id'])
        return id

    def load_vacancies(self, companies) -> List[Dict]:
        """Загружает вакансии для всех компаний из списка"""
        vacancies = []

        for company in companies:
            employer_id = self.__get_employer_ids(company)
            page = 0
            while True:
                params = {
                    'employer_id': employer_id,
                    'page': page,
                    'per_page': 100,
                    'archived': False
                }

                response = self.__session.get(
                    f"{self.__url}vacancies",
                    params=params,
                    headers=self.__headers
                )

                if not response.ok:
                    break

                data = response.json()
                vacancies.extend(data.get('items', []))

                # Проверка пагинации
                if page >= data.get('pages', 0) - 1:
                    break
                page += 1

        return [{
            'employer': item['employer']['name'],
            'title': item['name'],
            'salary_min': item['salary']['from'] if item['salary'] else None,
            'salary_max': item['salary']['to'] if item['salary'] else None,
            'url': item['alternate_url']
        } for item in vacancies]



if __name__ == "__main__":
    hh = HHAPI()

    vacancies = hh.load_vacancies(["Yandex", "СБЕР", "Avito", "VENTRA", "VK",
             "Альфа-банк", "ALTERNATIVA GAMES", "Т-Банк", "Код безопасности"])

    print(f"Найдено вакансий: {len(vacancies)}")
    for v in vacancies[:10]:
        print(v)
