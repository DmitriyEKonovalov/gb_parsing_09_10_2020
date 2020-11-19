"""
ДЗ 08
1)  Написать приложение, которое будет проходиться по указанному списку
    двух и/или более пользователей и собирать данные об их подписчиках и подписках.

2)  По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект
    нужно извлечь имя, id, фото (остальные данные по желанию). Фото можно дополнительно скачать.

3)  Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать,
    чтобы:
4)  Написать запрос к базе, который вернет список подписчиков только указанного пользователя
5)  Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

"""


from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import settings
from instagram.spiders.insta_parser import InstaParserSpider
from pymongo import MongoClient

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaParserSpider)
    process.start()
    print('_____________________________________')

    # ЗАДАНИЯ 4 и 5
    client = MongoClient('localhost', 27017)
    mongo_base = client.instagram
    collection = mongo_base['user_rel']

    # Написать запрос к базе, который вернет список подписчиков только указанного пользователя
    report1 = collection.find({'parsed_username': 'a.i_programmer', 'relation': 'subscriber'})
    for row in report1:
        print(row)

    # Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
    report2 = collection.find({'parsed_username': 'influence_coding', 'relation': 'subscribe'})
    for row in report2:
        print(row)

