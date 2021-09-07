from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroyparser.spiders.leroymerlinru import LeroymerlinruSpider
from leroyparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # answer = input('Введите запрос')
    process.crawl(LeroymerlinruSpider, query='ковер')
    process.start()