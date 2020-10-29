import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    """
    Паук для обработки superjob.ru
    """

    name = 'sjru'
    allowed_domains = ['spb.superjob.ru']
    start_urls = ['https://spb.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):
        vac_links_on_page = response.xpath('//a[contains (@class, "_6AfZ9")]/@href').extract()
        next_page_link = response.xpath('//span[@class="_3IDf-"]/@href').extract_first()
        for vac_link in vac_links_on_page:
            yield response.follow(vac_link, callback=self.parse_vacancy_page)
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)
        print()

    def parse_vacancy_page(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').extract_first()
        salary = response.xpath('//span[@class="_1OuF_ ZON4b"]//text()').extract()
        link = response.url
        yield JobparserItem(name=name, salary=salary, link=link, source='superjob.ru')
        print()
