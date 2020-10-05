# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    photo = scrapy.Field()
    likes = scrapy.Field()
    post = scrapy.Field()

    _id = scrapy.Field()

class InstFollowByItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    full_name = scrapy.Field()
    pic_url = scrapy.Field()
    is_private = scrapy.Field()
    is_verified = scrapy.Field()
    followed_by_viewer = scrapy.Field()
    requested_by_viewer = scrapy.Field()
    post = scrapy.Field()

    _id = scrapy.Field()
