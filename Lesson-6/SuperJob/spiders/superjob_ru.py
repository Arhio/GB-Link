import scrapy
from scrapy.http import HtmlResponse
from SuperJob.items import SuperJobItem

class SjruSpider(scrapy.Spider):
    name = 'superjob_ru'
    allowed_domains = ['russia.superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response:HtmlResponse):
        vacancies = response.css("a.icMQ_._6AfZ9::attr(href)").extract()
        for vacancy in vacancies:
            yield response.follow(vacancy, callback=self.vacancy_parse)

        next_page = response.css("a.icMQ_._1_Cht._3ze9n.f-test-button-dalshe.f-test-link-Dalshe::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']//text()").extract()
        proposal_min = 0
        proposal_max = 0
        proposal_currency = ''
        link = response.url
        main_link = 'superjob.ru'
        if len(salary) > 1:
            if len(salary) == 7:
                proposal_min = int(salary[0].replace(f'\xa0', f''))
                proposal_max = int(salary[4].replace(f'\xa0', f''))
                proposal_currency = salary[-1]
            elif (len(salary) >= 2) & (salary[0] == 'от'):
                a, b = salary[-1].replace(f'\xa000', f'00').replace(f'\xa030', f'30').replace(f'\xa0', f' ').split(' ')
                proposal_min = int(a)
                proposal_currency = b
            elif (len(salary) >= 2) & (salary[0] == 'до'):
                a, b = salary[-1].replace(f'\xa000', f'00').replace(f'\xa0', f' ').split(' ')
                proposal_max = int(a)
                proposal_currency = b

        yield SuperJobItem(name=name, proposal_min=proposal_min, proposal_max=proposal_max, proposal_currency=proposal_currency, link=link, main_link=main_link)
