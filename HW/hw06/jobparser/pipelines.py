# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from jobparser.items import JobparserItem
from scrapy import Spider


class JobparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item: JobparserItem, spider: Spider):
        collection = self.mongo_base[spider.name]
        item['min_salary'], item['max_salary'], item['currency'] = self.process_salary(item['salary'])
        # item.salary.popitem()  # удалим из элементов обработанный списко с зарплатой
        collection.insert(item)
        return item


    def cleanup_salary_list(self, salary_list: list):
        """
        Функция очистки массива с зарплатолй
        Удаляет пробелы между цифрами, пробелы с краев и пустые элементы списка
        Возвращает обработанный список
        """
        result_list = []
        for item in salary_list:
            item = item.strip().replace('\xa0', '').replace(' ', '')
            if item:
                result_list.append(item)
        return result_list


    def process_salary(self, salary: list):
        """
        Обработка зарплаты, состоящей из списка, элементов описания зарплаты на сайте, подходит для обоих сайтов.
        Известные шаблоны: "от ХХХ до руб.", "от ХХХ руб.", "до ХХХХ руб.", "ХХХХ-ХХХХ руб."
        """
        min_salary = None
        max_salary = None
        currency = None

        if salary:
            salary = self.cleanup_salary_list(salary)

            try:
                # подбираем шаблон
                for i in range(0, len(salary)):
                    # если встречаем значение 'от' то берем след элемент как минитмальную зарплату,
                    # а следующий за зарплатой элемент - как валюту
                    if salary[i] == 'от':
                        min_salary = int(''.join([i for i in salary[i+1] if i.isdigit()]))
                        currency = salary[i+2]

                    # если встречаем значение '-' то берем пред элемент как минитмальную зарплату,
                    # след за ним элемент - как ммаксимальную, а за максимальной - валюту
                    if salary[i] == '—':
                        min_salary = int(''.join([i for i in salary[i-1] if i.isdigit()]))
                        max_salary = int(''.join([i for i in salary[i+1] if i.isdigit()]))
                        currency = salary[i+2]

                    # если встречаем значение 'до' то берем след элемент как максимальную зарплату,
                    # а следующий за зарплатой элемент - как валюту
                    if salary[i] == 'до':
                        max_salary = int(''.join([i for i in salary[i+1] if i.isdigit()]))
                        currency = salary[i+2]

                    # здесь вытаскиваем валюту для superjob - она выбивается из шаблона
                    # (то в отдельном поле, то вместо с зарплатой)
                    # по алгоритму: находм '/' и в поле перед ним выбираем все не числовые символы
                    if salary[i] == '/':
                        currency = (''.join([i for i in salary[i-1] if not i.isdigit()]))

            except IndexError:
                pass  # игнорируем если зарплата вдруг не соответствует шаблону

        return min_salary, max_salary, currency
