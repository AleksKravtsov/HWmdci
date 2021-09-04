from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from Lesson_6.jobparser import settings
from Lesson_6.jobparser.spiders.hhru import HhruSpider
from Lesson_6.jobparser.spiders.superjobru import SuperjobruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SuperjobruSpider)

    process.start()