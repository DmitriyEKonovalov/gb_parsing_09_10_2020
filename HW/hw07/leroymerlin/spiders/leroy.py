import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = ['https://leroymerlin.ru/']

    def __init__(self, search):
        self.start_urls = [f'https://spb.leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page_link = response.xpath('//a[@navy-arrow="next"]/@href').extract_first()
        goods = response.xpath('//a[@slot="name"]')
        for good in goods:
            yield response.follow(good, callback=self.parse_goods_page)

        # debug для отладки, читаем только одну страницу
        # next_page_link = None
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_goods_page(self, response: HtmlResponse):
        """
        Парсинг страницы с товаром
        """
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', '//h1[@slot="title"]/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('props', '//section[@id="nav-characteristics"]')
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[@media=" only screen and (min-width: 1024px)"]/@data-origin')
        yield loader.load_item()

