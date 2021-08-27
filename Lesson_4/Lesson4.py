import requests
from lxml import html
import pandas as pd
from pprint import pprint
from pymongo import MongoClient

pd.options.display.max_columns = 5

url = 'https://yandex.ru/news/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
responce = requests.get(url, headers=headers)
dom_html = html.fromstring(responce.text)

names = dom_html.xpath("//div[contains(@class, 'news-top-flexible-stories')]//div[@class='mg-card__annotation']//text()")
links = dom_html.xpath("//div[contains(@class, 'news-top-flexible-stories')]//a[@class='mg-card__link']//@href")
date = dom_html.xpath("//div[contains(@class, 'news-top-flexible-stories')]//span[@class='mg-card-source__time']/text()")
course = dom_html.xpath("//div[contains(@class, 'news-top-flexible-stories')]//a[@rel='noopener']/text()")
list_data = []
for i in range(len(names)):
    list_data.append([names[i], date[i], course[i], links[i]])


connect = MongoClient('localhost', 27017)
data = pd.DataFrame(list_data, columns=['Новость', 'Дата', 'Источник', 'Ссылка'])
db = connect['news']
db.yandex_news.delete_many({})
db.yandex_news.insert_many(data.to_dict('records'))
pprint(data)

