# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import hashlib
from scrapy.utils.python import to_bytes
from pymongo import MongoClient


class LeroymerlinPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert(item)
        return item


class LeroymerlinPhotoPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as e:
                    print(e)
        return item

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [i[1] for i in results if i[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        img_folder = item['name']
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        result = f'/{img_folder}/{image_guid}.jpg'
        return result
