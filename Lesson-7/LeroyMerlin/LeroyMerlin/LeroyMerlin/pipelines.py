# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
from itemadapter import ItemAdapter
import scrapy
from scrapy.utils.python import to_bytes
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class LeroymerlinPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.LeroyMerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        # doc = dict(item)
        collection.insert_one(item)

        return item

class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        path = item['path']
        search = item['search']
        m = f'{path}/{search}'
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request( img, meta=item)
                except Exception as e:
                    print(e)


    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):

        path = f'{request.meta["search"]}/{request.meta["path"]}/full/{ hashlib.sha1(to_bytes(request.url )).hexdigest() }.jpg'
        return path
