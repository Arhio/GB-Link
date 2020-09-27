# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join

def refactor_link(value):
    if value:
        return value #.upper()


def refactor_specifications(value):
    if value:
        return [o for o in [str(p).replace('\n', '').strip() for p in value] if o != '']

class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    discription = scrapy.Field(output_processor=TakeFirst())
    specifications = scrapy.Field(input_processor=Join())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())

    photos = scrapy.Field(input_processor=MapCompose(refactor_link))

    _id = scrapy.Field()

