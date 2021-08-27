from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd



#Функция проходит по всем возможным страницам и собирает вакансии
def parser_hh(vacancy):

    vacancy_date = []

    params = {
        'text': vacancy,
        'page': ''
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.147'
    }

    link_hh = 'https://hh.ru/search/vacancy'

    response = requests.get(link_hh, params=params, headers=headers)

    if response.ok:
        parsed_html = bs(response.text,'html.parser')

        page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = 1
        else:
            last_page = page_block.find_all('a', {'class': 'bloko-button'})
            last_page = int(last_page[len(last_page)-2].find('span').getText())

    for page in range(0, last_page):
        params['page'] = page
        response = requests.get(link_hh, params=params, headers=headers)

        if response.ok:
            parsed_html = bs(response.text,'html.parser')

            vacancy_items = parsed_html.find_all('div', {'class': 'vacancy-serp-item'})
            #Здесь вызывается функция и она парсит одну страницу, потом следующую и т.д
            for item in vacancy_items:
                vacancy_date.append(parser_item_hh(item))

    return vacancy_date

'''Функция парсит вакансии и отбирает нужные данные/атрибуты,
в качестве входного параметра берутся вакансии одной страницы'''
def parser_item_hh(item):

    vacancy_dict = {}

    vacancy_name = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}) \
            .getText().replace(u'\xa0', u' ')

    vacancy_dict['vacancy_name'] = vacancy_name

    company_name = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})

    if company_name:
        company_name = company_name.getText().replace(u'\xa0', u' ')
    vacancy_dict['company_name'] = company_name

    city = item.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}) \
        .getText() \
        .split(', ')[0]

    vacancy_dict['city'] = city

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

        salary_currency = salary[len(salary)-1]

    vacancy_dict['salary_min'] = salary_min
    vacancy_dict['salary_max'] = salary_max
    vacancy_dict['salary_currency'] = salary_currency

    vacancy_link = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']

    vacancy_dict['vacancy_link'] = vacancy_link
    vacancy_dict['site'] = 'hh.ru'

    return vacancy_dict

def parser_vacancy(vacancy):

    vacancy_data = []
    vacancy_data.extend(parser_hh(vacancy))
    vacancy_data = filter(None, vacancy_data)

    df = pd.DataFrame(vacancy_data)

    return df

df = parser_vacancy('python')
result = df.to_json('collected_data.json', orient='records', force_ascii=False)

print("Finished!")