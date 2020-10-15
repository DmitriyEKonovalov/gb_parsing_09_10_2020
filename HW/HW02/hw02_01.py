"""
Домашнее задание
Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы) с сайтов Superjob и HH.
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату (отдельно минимальную и максимальную).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия.

По желанию можно добавить ещё параметры вакансии
(например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas.

"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pprint import pprint

result = []  # переменная в которую сохраняяется резулльтат парсинга

# парсим сайт hh.ru
# задаем первоначальные параметры
start_link ='https://spb.hh.ru/'
action = 'search/vacancy?'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
}
params = {
    'st': 'searchVacancy',
    'text': 'методолог', # %D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%BB%D0%BE%D0%B3
    'area': '2',
    'salary': '',
    'currency_code': 'RUR',
    'experience': 'doesNotMatter',
    'order_by': 'relevance',
    'search_period': '0',
    'items_on_page': '50',
    'no_magic': 'true',
    'L_save_area': 'true',
    'page': '0'
}

while True:
    response = requests.get(start_link + action, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    # vac_list = soup.find_all('div', {'data-qa':['vacancy-serp__vacancy']})  # выбирает только обычные вакансии
    vacancy_list = soup.find_all('div', {'class':['vacancy-serp-item']})  # выбирает все, включая премиум
    # источник вакансии
    vac_source = start_link

    for vacancy in vacancy_list:
        # парсим название вакансии
        vac_name = vacancy.find('a', {'data-qa': ['vacancy-serp__vacancy-title']}).get_text()
        # парсим зарплату
        vac_salary = vacancy.find('span', {'data-qa': ['vacancy-serp__vacancy-compensation']})
        vac_min_salary = None
        vac_max_salary = None
        if vac_salary:
            if vac_salary.text.find('от') != -1:
                vac_min_salary = vac_salary.text.split(' ')[1]
            if vac_salary.text.find('до') != -1:
                vac_max_salary = vac_salary.text.split(' ')[1]
            if vac_salary.text.find('-') != -1:
                vac_min_salary = vac_salary.text.split('-')[0]
                vac_max_salary = vac_salary.text.split('-')[1]
        # парсим работодателя
        vac_employer = vacancy.find('a', {'data-qa': ['vacancy-serp__vacancy-employer']})
        # парсим место
        vac_city = vacancy.find('span', {'data-qa': ['vacancy-serp__vacancy-address']})
        vac_metro = vacancy.find('span', {'class': ['metro-station']})
        vac_place = vac_city.text if vac_city else '' + ', ' if vac_city and vac_metro else '' + vac_metro.text if vac_metro else ''
        # парсим ссылку на вакансию
        vac_link = vacancy.find('a', {'class': ['bloko-link HH-LinkModifier']})['href']
        # добавляем данные по элементу в result
        result.append({'name': vac_name,
                       'min salary': vac_min_salary,
                       'max salary': vac_max_salary,
                       'employer': vac_employer.text if vac_employer else '',
                       'place': vac_place,
                       'link': vac_link,
                       'source': vac_source
                       })
    # проверка на наличие кнопки "дальше", если есть, то меняем номер страницы и запускаем парсинг снова, иначе выход
    next_link = soup.find('a', {'data-qa': ['pager-next']})
    if next_link:
        # здесь можно было бы понадежнее сделать - вместо инкремента выбирать номера страницы из ссылки
        params['page'] = str(int(params['page']) + 1)
    else:
        break


# парсим сайт superjob.ru
# задаем первоначальные параметры
start_link ='https://spb.superjob.ru/'
action = 'vacancy/search/?'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
}
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
        # парсим название вакансии
        vac_title = vacancy.find('div', {'class': ['_3mfro PlM3e _2JVkc _3LJqf']})
        vac_name = vac_title.get_text() if vac_title else ''
        vac_link = start_link + vac_title.next['href'] if vac_title else ''

        # парсим зарплату
        vac_salary = vacancy.find('span', {'class': ['_3mfro _2Wp8I PlM3e _2JVkc _2VHxz']})
        vac_min_salary = ''
        vac_max_salary = ''
        if vac_salary:
            vac_salary = vac_salary.text
            if vac_salary.find('от') != -1:
                vac_min_salary = ''.join([char for char in vac_salary if char.isdigit()])
            if vac_salary.find('до') != -1:
                vac_max_salary = ''.join([char for char in vac_salary if char.isdigit()])
            if vac_salary.find('—') != -1:
                vac_min_salary = ''.join([char for char in vac_salary.split('—')[0] if char.isdigit()])
                vac_max_salary = ''.join([char for char in vac_salary.split('—')[1] if char.isdigit()])

        # парсим место
        vac_place = vacancy.find('span', {'class': ['clLH5']})
        vac_place = vac_place.next_sibling
        vac_place = vac_place.get_text() if vac_place else ''

        # парсим работодателя
        vac_employer = vacancy.find('span', {'class': ['_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI']})
        vac_employer = vac_employer.get_text() if vac_employer else ''

        # добавляем данные по элементу в result
        result.append({'name': vac_name,
                       'min salary': vac_min_salary,
                       'max salary': vac_max_salary,
                       'employer': vac_employer,
                       'place': vac_place,
                       'link': vac_link,
                       'source': vac_source
                       })
    # конец цикла парсинга страницы

    # проверка на наличие кнопки "дальше", если есть, то меняем номер страницы и запускаем парсинг снова, иначе выход
    next_link = soup.find('a', {'class': ['icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe']})
    if next_link:
        # здесь тоже можно было бы понадежнее сделать - вместо инкремента выбирать номера страницы из ссылки
        params['page'] = str(int(params['page']) + 1)
    else:
        break


db = pd.DataFrame(result)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

pprint(db)
