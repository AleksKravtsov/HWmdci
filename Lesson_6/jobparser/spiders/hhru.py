import scrapy
from scrapy.http import HtmlResponse
from Lesson_6.jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=data+scientist&area=1',
                  'https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=data+scientist&area=2']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vac_name = response.xpath("//h1/text()").get()
        # salary = response.xpath("//p[@class='vacancy-salary']/span/text()").get()
        vac_salary = response.css("p.vacancy-salary span::text").get()
        vac_url = response.url
        item = JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)
        yield item
