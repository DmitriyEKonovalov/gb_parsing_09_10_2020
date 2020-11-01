# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.selector import Selector

def parse_props(value):
    """
    Функция обработки свойств товара
    Принимает html селектор со всеми свойствами в текствовом виде
    Возвращает словарь свойств
    """
    if value:
        # преобразовываем в selector и вытаскиваем список селекторов со свойствами
        r = Selector(text=value)
        sel_list = r.xpath('//div[@class = "def-list__group"]')
        result = {}
        for sel in sel_list:
            # вытаскиваем название свойства
            k = sel.xpath('.//dt/text()').extract_first()
            # вытаскиваем значение свойства и очищаем его
            v_str = sel.xpath('.//dd/text()').extract_first()
            v_str = ''.join(i.strip().replace(',', '.') for i in v_str.split('\n'))
            # значение свойства пробуем привести к числу, если исключение - оставляем строковым
            try:
                v = float(v_str)
            except ValueError:
                v = v_str
            result[k] = v
        value = result
        return value


def convert_price(value):
    """
    Функция преобразования цены в цифровое значение
    """
    if value:
        value = value.replace(',', '.').replace(' ', '')
        try:
            result = float(value)
        except ValueError:
            # в случае ошибки преобразование сохраняем исходное значение
            result = value
    return result



class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_price), output_processor=TakeFirst())
    props = scrapy.Field(input_processor=MapCompose(parse_props), output_processor=TakeFirst())
    photos = scrapy.Field()
    # currency = scrapy.Field()
    # unit = scrapy.Field()
