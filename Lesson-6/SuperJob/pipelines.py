# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class SuperJobPipeline:
    def __init__(self):
        client = MongoClient('localhost',27017)
        self.mongobase = client.vacancy180920

    def process_item(self, item, spider):
        vacansy = dict(item)
        collection = self.mongobase[spider.name]
        collection.insert_one(vacansy)
        return item