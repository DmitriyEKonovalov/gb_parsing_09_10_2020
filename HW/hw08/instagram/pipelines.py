# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from instagram.items import InstagramItem
from scrapy import Spider
from pymongo import MongoClient


class InstagramPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram
        # выбрал решение сохранять подписчиков и подписки в одну коллекцию
        # в одной коллекции будет удобнее исследовать сложные связи между пользователями
        # мы ведь, предположительно, для этого парсим? :)
        self.collection = self.mongo_base['user_rel']

    def process_item(self, item: InstagramItem, spider: Spider):
        self.collection.insert(item)
        return item

