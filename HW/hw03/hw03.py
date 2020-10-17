"""
Домашнее задание
Урок 3. Системы управления базами данных MongoDB и SQLite в Python

1.
Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
и реализовать функцию, записывающую собранные вакансии в созданную БД.

2.
Написать функцию, которая производит поиск и выводит на экран вакансии
с заработной платой больше введённой суммы.

3.
Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

"""

from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from pprint import pprint


def db_init():
    """
    Задание 1
    Функция инициализации базы данных mongodb
    Возвращает коллекцию базы данных
    """
    client = MongoClient('127.0.0.1', 27017)
    database = client['vacancies']
    return database


def find_vacancies_gt_sum(db_col, min_sum):
    """
    Задание 2
    функция поиска списка вакансий бс минимально зп больше заданного значения
    В аргументах получает коллекцию данных mongodb и сумму для поиска
    Возвращает список с вакансиями
    """
    return list(vac_col.find({"min salary": {"$gt": min_sum}}))[:]


def save_vac_if_not_exist(db_col, vac):
    """
    Задание 3
    Функция записывает вакансию в базу, предварительно проверяя наличие ее в базе
    В аргументах передается коллекция в базе и словарь с данными о вакансии
    возвращает 1 если вакансии не было и была сохранена, 0 если уже есть
    """
    if not db_col.find_one(vac):
        db_col.insert_one(vac)
        return 1
    else:
        return 0


def refine_vac_salary(vac_sal_tag):
    """
    Функция для очистки от лишних символов и вытаскивания суммы зарплвты от и до,
    принимает tag и возвращает set из двух int
    """
    s = vac_sal_tag.text if vac_sal_tag else ''  # исходная строка
    sd = ''.join([char for char in s if char.isdigit() or char in ['-']])  # строка очищенная от лишних символов
    min_s = None
    max_s = None
    if s:
        if s.find('от') >= 0:
            min_s = int(sd) if sd else None  # на случай если появляются слова типа 'по ДОговоренности'
        if s.find('до') >= 0:
            max_s = int(sd) if sd else None
        if s.find('-') >= 0:
            min_s, max_s = int(sd.split('-')[0]), int(sd.split('-')[1])
    return min_s, max_s


db = db_init()
vac_col = db.vacancies

total_vac_count = 0     # количество всех просмотренных вакансий с сайтов
inserted_vac_count = 0  # количество новых вакансий, которые были добавлены

# заголовок для запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

# -----------------------------
# парсим сайт hh.ru с параметрами
start_link ='https://spb.hh.ru/'
action = 'search/vacancy?'
params = {
    'st': 'searchVacancy',
    'text': 'методолог', 
    'area': '2',
    'salary': '',
    'currency_code': 'RUR',
    'experience': 'doesNotMatter',
    'search_period': '0',
    'items_on_page': '50',
    'no_magic': 'true',
    'L_save_area': 'true',
    'page': '0'
}

while True:
    response = requests.get(start_link + action, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', {'class':['vacancy-serp-item']})  # выбирает все, включая премиум

    for vacancy in vacancy_list:
        # парсим название вакансии
        vac_name = vacancy.find('a', {'data-qa': ['vacancy-serp__vacancy-title']}).get_text()

        # парсим зарплату
        vac_salary = vacancy.find('span', {'data-qa': ['vacancy-serp__vacancy-compensation']})
        vac_min_salary, vac_max_salary = refine_vac_salary(vac_salary)

        # парсим работодателя
        vac_employer = vacancy.find('a', {'data-qa': ['vacancy-serp__vacancy-employer']})
        vac_employer = vac_employer.text if vac_employer else ''

        # парсим место
        vac_city = vacancy.find('span', {'data-qa': ['vacancy-serp__vacancy-address']})
        vac_metro = vacancy.find('span', {'class': ['metro-station']})
        vac_place = vac_city.text if vac_city else '' + ', ' if vac_city and vac_metro else '' + vac_metro.text if vac_metro else ''
        
        # парсим ссылку на вакансию
        vac_link = vacancy.find('a', {'class': ['bloko-link HH-LinkModifier']})['href']

        # добавляем данные с проверкой
        inserted_vac_count += save_vac_if_not_exist(vac_col,
                                                    {'name': vac_name,
                                                     'min salary': vac_min_salary,
                                                     'max salary': vac_max_salary,
                                                     'employer': vac_employer,
                                                     'place': vac_place,
                                                     'link': vac_link,
                                                     'source': start_link
                                                     })
        total_vac_count += 1
    # конец цикла парсинга страницы

    # проверка на наличие кнопки "дальше", если есть, то меняем номер страницы и запускаем парсинг снова, иначе выход
    next_link = soup.find('a', {'data-qa': ['pager-next']})
    if next_link:
        params['page'] = str(int(params['page']) + 1)
    else:
        break


# -----------------------------
# парсим сайт superjob.ru c параметрами
start_link ='https://spb.superjob.ru/'
action = 'vacancy/search/?'
params = {
    'keywords': 'методолог',
    'page': '1'
}

while True:
    response = requests.get(start_link + action, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    vacancy_list = soup.find_all('div', {'class':['iJCa5 f-test-vacancy-item _1fma_ undefined _2nteL']})
    # источник вакансии
    vac_source = start_link

    # парсинг страницы
    for vacancy in vacancy_list:

        vac_title = vacancy.find('div', {'class': ['_3mfro PlM3e _2JVkc _3LJqf']})
        vac_name = vac_title.get_text() if vac_title else ''  # парсим название вакансии
        vac_link = start_link + vac_title.next['href'] if vac_title else ''

        # парсим зарплату
        vac_salary = vacancy.find('span', {'class': ['_3mfro _2Wp8I PlM3e _2JVkc _2VHxz']})
        vac_min_salary, vac_max_salary = refine_vac_salary(vac_salary)

        # парсим место
        vac_place = vacancy.find('span', {'class': ['clLH5']})
        vac_place = vac_place.next_sibling
        vac_place = vac_place.get_text() if vac_place else ''

        # парсим работодателя
        vac_employer = vacancy.find('span', {'class': ['_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI']})
        vac_employer = vac_employer.get_text() if vac_employer else ''

        # добавляем данные с проверкой
        inserted_vac_count += save_vac_if_not_exist(vac_col, {
                                                    'name': vac_name,
                                                    'min salary': vac_min_salary,
                                                    'max salary': vac_max_salary,
                                                    'employer': vac_employer,
                                                    'place': vac_place,
                                                    'link': vac_link,
                                                    'source': vac_source
                                                    })
        total_vac_count += 1
    # конец цикла парсинга страницы

    # проверка на наличие кнопки "дальше", если есть, то меняем номер страницы и запускаем парсинг снова, иначе выход
    next_link = soup.find('a', {'class': ['icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe']})
    if next_link:
        params['page'] = str(int(params['page']) + 1)
    else:
        break

print(f'Добавлено новых вакансий: {inserted_vac_count} из {total_vac_count} просмотренных')

# проверяем поиск по базе
user_input = input('Введите минимальную сумму зарплаты для поиска вакансий: ')
if user_input.isdigit():
    pprint(find_vacancies_gt_sum(vac_col, int(user_input)))
else:
    pprint("необходимо ввести число")

