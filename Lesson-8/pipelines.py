# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import scrapy
from scrapy.utils.python import to_bytes
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline

from items import InstaparserItem, InstFollowByItem


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.Inst


    def process_item(self, item, spider):
        if type(item) is InstaparserItem:
            collection = self.mongo_base['instagram_posts']
            collection.insert_one(item)
        if type(item) is InstFollowByItem:
            collection = self.mongo_base['instagram_follows']
            collection.insert_one(item)
        return item
