import scrapy
from scrapy.http import HtmlResponse
from LeroyMerlin.LeroyMerlin.LeroyMerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LMSpider(scrapy.Spider):
    name = 'leroymerlin_ru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self,params):
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{params[0]}?page=1']
        self.search = params[0]

    def parse(self, response:HtmlResponse):
        items = response.xpath("//a[@slot='name']/@href").extract()

        for item in items:
            yield response.follow('http://leroymerlin.ru' + item, callback=self.item_parse)

        next_page = response.xpath("//div[ @class ='next-paginator-button-wrapper']//a//@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)



    def item_parse(self, response:HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', "//h1//text()")
        loader.add_xpath('discription', "//uc-pdp-section-vlimited/div//text()")
        loader.add_value('specifications', ['|' + o for o in [str(p).replace('\n', '').strip() for p in response.xpath("//uc-pdp-section-vlimited/dl//text()").extract()] if o != ''])
        loader.add_value('link', response.url)
        loader.add_xpath('price', "//meta[@itemprop='price']/@content")

        loader.add_xpath('photos', "//picture[@slot='pictures']/source[contains(@srcset, '2000')]/@srcset")
        yield loader.load_item()