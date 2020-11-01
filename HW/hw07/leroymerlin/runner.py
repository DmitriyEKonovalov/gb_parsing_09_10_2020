"""
ДЗ 07
1) Взять любую категорию товаров на сайте Леруа Мерлен.
Собрать с использованием ItemLoader следующие данные:
● название;
● все фото;
● параметры товара в объявлении;
● ссылка;
● цена.

С использованием output_processor и input_processor реализовать очистку и преобразование данных.
Цены должны быть в виде числового значения.

2)Написать универсальный обработчик параметров объявлений,
который будет формировать данные вне зависимости от их типа и количества.

3)Реализовать хранение скачиваемых файлов в отдельных папках,
каждая из которых должна соответствовать собираемому товару

"""


from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings
from leroymerlin.spiders.leroy import LeroySpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroySpider, search='стеллаж')

    process.start()
