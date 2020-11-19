# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()  # создание поля id искусственно, для добадления в mongodb
    name = scrapy.Field()
    salary = scrapy.Field()  # оставил исходное поле с зарплатой для отладки
    link = scrapy.Field()
    source = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    currency = scrapy.Field()




