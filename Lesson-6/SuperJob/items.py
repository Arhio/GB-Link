# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SuperJobItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    proposal_min = scrapy.Field()
    proposal_max = scrapy.Field()
    proposal_currency = scrapy.Field()
    link = scrapy.Field()
    main_link = scrapy.Field()