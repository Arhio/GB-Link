from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from LeroyMerlin.LeroyMerlin.LeroyMerlin import settings
from LeroyMerlin.LeroyMerlin.LeroyMerlin.spiders.LM import LMSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    # answer = input('Введите поисковый запрос')
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LMSpider, params=['lyustry'])

    process.start()


# def func1(*args, **kwargs):