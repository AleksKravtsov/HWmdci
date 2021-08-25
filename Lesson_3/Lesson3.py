from bs4 import BeautifulSoup as bs
from pprint import pprint
from pymongo import MongoClient
import re
import requests


# Класс парсера который работает с Mongo
class ParsingJob:

    def __init__(self, ip, port, db_name, collection_name):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }
        self.link_hh = 'https://hh.ru/search/vacancy'
        self.mongodb = MongoClient(ip, port)
        self.db = self.mongodb[db_name]
        self.collection = self.db[collection_name]

    # Максимальная ЗП
    def print_salary_max_gt(self, salary):
        objects = self.collection.find({'salary_max': {'$gt': salary}})
        for obj in objects:
            pprint(obj)

    # Минимальная ЗП
    def print_salary_min_gt(self, salary):
        objects = self.collection.find({'salary_min': {'$gt': salary}})
        for obj in objects:
            pprint(obj)

    # Вызыватель суперпарсера
    def search_job(self, vacancy):
        self.parser_hh(vacancy)
        # self.parser_superjob(vacancy)

    # Проверка на существование вакансии для исключения дублей
    def is_exists(self, name_tags, field):
        return bool(self.collection.find_one({name_tags: {"$in": [field]}}))

    # Парсер HH по страницам
    def parser_hh(self, vacancy):
        params = {
            'text': vacancy,
            'page': ''
        }

        response_hh = requests.get(self.link_hh, params=params, headers=self.headers)

        if response_hh.ok:
            parsed_html = bs(response_hh.text, 'html.parser')

            page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
            if not page_block:
                last_page = 1
            else:
                last_page = page_block.find_all('a', {'class': 'bloko-button'})
                last_page = int(last_page[len(last_page) - 2].find('span').getText())

        for page in range(0, last_page):
            params['page'] = page
            response_hh = requests.get(self.link_hh, params=params, headers=self.headers)

            if response_hh.ok:
                parsed_html = bs(response_hh.text, 'html.parser')

                vacancy_items = parsed_html.find_all('div', {'class': 'vacancy-serp-item'})
                # Здесь вызывается функция и она парсит одну страницу, потом следующую и т.д
                for item in vacancy_items:
                    vacancy = self.parser_item_hh(item)
                    self.collection.update_one({'vacancy_link': vacancy['vacancy_link']}, {'$set': vacancy}, upsert=True)


    # Распарсивание вакансии HH Из страницы
    def parser_item_hh(self, item):

        vacancy_data = {}

        vacancy_name = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}) \
            .getText().replace(u'\xa0', u' ')

        vacancy_data['vacancy_name'] = vacancy_name

        company_name = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})

        if company_name:
            company_name = company_name.getText().replace(u'\xa0', u' ')
        vacancy_data['company_name'] = company_name

        city = item.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}) \
            .getText() \
            .split(', ')[0]

        vacancy_data['city'] = city

        # salary
        salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText().replace(u'\u202f', u'')
            salary = salary.replace('–', '')
            salary = re.split(r'\s', salary)

            if salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
            elif salary[0] == 'от':
                salary_min = int(salary[1])
                salary_max = None
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[2])

            salary_currency = salary[len(salary) - 1]

        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency

        vacancy_link = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']

        vacancy_data['vacancy_link'] = vacancy_link
        vacancy_data['site'] = 'hh.ru'

        return vacancy_data


vacancy_db = ParsingJob('127.0.0.1', 27017, 'vacancy',
                        'vacancy_db')  # Установка соединения с Mongo и создание коллекций

# Заполнение коллекции и вывод каждый
# Каждый вызов добавляет новые вакансии, дубли заменяются
vacancy = 'Data'
vacancy_db.search_job(vacancy)
objects = vacancy_db.collection.find().limit(1)
for obj in objects:
    pprint(obj)

print(' Ниже зарплаты \n')
vacancy_db.print_salary_max_gt(100000)  # Максимальная зп
vacancy_db.print_salary_min_gt(50000) # минимальная ЗП