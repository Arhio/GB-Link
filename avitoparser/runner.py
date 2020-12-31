from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from avitoparser import settings
from avitoparser.spiders.avitoru import AvitoruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    # answer = input('Введите поисковый запрос')
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(AvitoruSpider,params=['холодильник','moskva'])

    process.start()


# def func1(*args, **kwargs):