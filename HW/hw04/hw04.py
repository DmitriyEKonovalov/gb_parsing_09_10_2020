"""
Написать приложение, которое собирает основные новости с сайтов
news.mail.ru, lenta.ru, yandex-новости.

Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.

"""

import requests
from lxml import html
from pymongo import MongoClient
from datetime import datetime as dt


def save_news_if_not_exist(db_col, title):
    """
    Функция записывает новость в базу, предварительно проверяя наличие в базе
    В аргументах передается коллекция в базе и словарь с данными о новости
    возвращает 1 если вакансии не было и была сохранена, 0 если уже есть
    """
    if not db_col.find_one(title):
        db_col.insert_one(title)
        return 1
    else:
        return 0


def parsing_news_mail_ru(db_col):
    """
      Функция парсинга new.mail.ru
      В параметрах принимает ссылку на коллекцию в базе,
      для запроса использует глобальные переменные
      ничего не возвращает, но записывает данные в коллекцию
    """

    def extract_source_and_time(news_link: str):
        """
        Внутренняя функция, для перехода по ссылке ивытасиквания из статьи времени публикации и источника
        Возвращает набор из двух значений: дату и источник
        """
        # article_response = requests.get(news_link, headers=headers)
        article_response = requests.get('https://news.mail.ru/society/43830362/', headers=headers)
        article = html.fromstring(article_response.text)

        post_date = article.xpath("//span[@datetime]/@datetime")
        post_source = article.xpath("//span[@class='note']/span[contains(text(), 'источник')]/../a/span/text()")
        # для простоты будем считать, что формат даты всегда одинаковый
        # проверяем ее на шаблон, если не подходит, то считаем, что даты нет
        # Здесь формат ISO '2020-10-21T09:49:34+03:00'
        try:
            post_date = dt.fromisoformat(post_date[0])
        except ValueError:
            post_date = ''

        return post_date, post_source[0] if post_source else ''

    start_link = 'https://news.mail.ru'
    response = requests.get(start_link, headers=headers)
    page = html.fromstring(response.text)  # главная страница
    main_news = page.xpath("//div[contains(@class, 'daynews__item')]")  # блок с новостями
    for title in main_news:
        t_name = title.xpath(".//span[contains(@class, 'photo__title')]/text()")
        t_link = title.xpath(".//a[contains(@class, 'photo')]/@href")
        t_date, t_source = extract_source_and_time(t_link)
        news = {'name': t_name[0] if t_name else '',
                'link': t_link[0] if t_link else '',
                'date': t_date,
                'source': t_source
                }
        save_news_if_not_exist(db_col, news)


def parsing_news_lenta_ru(db_col):
    """
      Функция парсинга lenta.ru
      В параметрах принимает ссылку на коллекцию в базе,
      для запроса использует глобальные переменные
      ничего не возвращает, но записывает данные в коллекцию
    """
    MONTHS = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                        'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
    start_link = 'https://lenta.ru/'
    response = requests.get(start_link, headers=headers)
    page = html.fromstring(response.text)  # главная страница
    main_news = page.xpath("//section[contains(@class, 'b-top7-for-main')]"
                           "/div[contains(@class, 'span4')]"
                           "/div[contains(@class, 'item')]//time/..")  # список новостей
    for title in main_news:
        t_name = title.xpath("./text()")
        t_link = title.xpath("./@href")
        t_date = title.xpath(".//@datetime")
        # для простоты будем считать, что формат даты всегда одинаковый
        # проверяем ее на шаблон, если не подходит, то считаем, что даты нет
        # Здесь формат ' 17:10, 22 октября 2020'
        try:
            month_name = t_date[0].strip().split(' ')[2]
            t_date = t_date[0].replace(month_name, MONTHS[month_name])
            t_date = dt.strptime(t_date, ' %H:%M, %d %m %Y')
        except (ValueError, IndexError):
            t_date = ''

        news = {'name': t_name[0] if t_name else '',
                'link': start_link + t_link[0] if t_link else '',
                'date': t_date,
                'source': 'lenta.ru'
                }
        save_news_if_not_exist(db_col, news)


def parsing_yandex_news(db_col):
    """
      Функция парсинга https://yandex.ru/news
      В параметрах принимает ссылку на коллекцию в базе,
      для запроса использует глобальные переменные
      ничего не возвращает, но записывает данные в коллекцию
    """
    start_link = 'https://yandex.ru/news'
    response = requests.get(start_link, headers=headers)
    page = html.fromstring(response.text)  # главная страница
    main_news = page.xpath("//div[contains(@class, 'news-top-stories')]/div")  # список новостей
    for title in main_news:
        t_name = title.xpath(".//h2[@class ='news-card__title']/text()")
        t_link = title.xpath(".//a[@href]/@href")
        t_source = title.xpath(".//span[@class='mg-card-source__source']/a/text()")
        t_date = title.xpath(".//span[@class='mg-card-source__time']/text()")
        # для простоты будем считать, что формат даты всегда одинаковый
        # проверяем ее на шаблон, если не подходит, то считаем, что даты нет
        # Здесь по главным новостям только время, формат '17:10' добаляем текущую дату
        try:
            t_time = dt.time(dt.strptime(t_date[0], '%H:%M'))
            t_date = dt(year=dt.now().year, month=dt.now().month, day=dt.now().day,
                        hour=t_time.hour, minute=t_time.minute)
        except (ValueError, IndexError):
            t_date = ''

        news = {'name': t_name[0] if t_name else '',
                'link': start_link + t_link[0] if t_link else '',
                'date': t_date,
                'source': t_source[0] if t_source else ''
                }
        save_news_if_not_exist(db_col, news)


# параметры и заголовок для запроса одинаковые для всех сайтов, поэтому для простоты будут глобальные переменные
params = {}
headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
           }

# база данных
client = MongoClient('127.0.0.1', 27017)
news_db = client['news']
news_col = news_db.news_colection

# начинаем парсинг
parsing_news_mail_ru(news_col)
parsing_news_lenta_ru(news_col)
parsing_yandex_news(news_col)
