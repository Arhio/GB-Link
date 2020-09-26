import scrapy
from scrapy.http import HtmlResponse
from SuperJob.items import SuperJobItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://izhevsk.hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=python&showClusters=true']

    def parse(self, response:HtmlResponse):
        vacancies = response.css("div.vacancy-serp-item__row_header a.bloko-link::attr(href)").extract()
        for vacancy in vacancies:
            yield response.follow(vacancy,callback=self.vacancy_parse)

        next_page = response.css("a.HH-Pager-Controls-Next::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']//text()").extract()
        proposal_min = 0
        proposal_max = 0
        proposal_currency = ''
        link = response.url
        main_link = 'hh.ru'

        for i in range(len(salary)):
            if salary[i].replace(' ', '') == 'от':
                proposal_min = int(salary[i+1].replace(f'\xa0', f''))
            if salary[i].replace(' ', '') == 'до':
                proposal_max = int(salary[i+1].replace(f'\xa0', f''))
            if i == (len(salary) - 2):
                proposal_currency = salary[i]

        yield SuperJobItem(name=name, proposal_min=proposal_min, proposal_max=proposal_max, proposal_currency=proposal_currency, link=link, main_link=main_link)
