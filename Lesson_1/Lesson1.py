# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

import requests
import json

url = 'https://api.github.com'
user='AleksKravtsov'

r = requests.get(f'{url}/users/{user}/repos')
with open('data.json', 'w') as f:
    json.dump(r.json(), f)

for i in r.json():
    print(i['name'])

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.

#63c2465baefa4d3217199fcc546ea060

from pprint import pprint
city = 'Boston'

url = 'http://api.openweathermap.org/data/2.5/weather'
my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
              'Accept': '*/*'}
my_params = {'q': city,
             'appid': '63c2465baefa4d3217199fcc546ea060'}

response = requests.get(url, params=my_params, headers=my_headers)
j_data = response.json()

with open('data_2.json', 'w') as f:
    json.dump(j_data, f)


