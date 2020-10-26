"""
1.
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
и сложить данные о письмах в базу данных
(от кого, дата отправки, тема письма, текст письма полный)
"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from pymongo import MongoClient
from datetime import datetime as dt
from datetime import timedelta as td

# Инициализируем базу данных
client = MongoClient('127.0.0.1', 27017)
mail_db = client['mails']
mails = mail_db.mails

# Запускаем драйвер и переходим на страницу
driver = webdriver.Chrome(executable_path='../../venv/chromedriver.exe')
driver.get('https://mail.ru/')

# Вводим логин
login = driver.find_element_by_id('mailbox:login-input')
login.send_keys('study.ai_172')

# Выбираем домен
domain = driver.find_element_by_id('mailbox:domain')
domains_list = Select(domain)
domains_list.select_by_visible_text('@mail.ru')

# Снимаем галку с "сохранить пароль"
save_pass_checkbox = driver.find_element_by_id('mailbox:saveauth')
if save_pass_checkbox.is_selected():
    save_pass_checkbox.click()

# Вводим пароль
pass_button = driver.find_element_by_id('mailbox:submit-button')
pass_button.click()
time.sleep(2)
pass_input = driver.find_element_by_id('mailbox:password-input')
pass_input.send_keys('NextPassword172')

submit_button = driver.find_element_by_id('mailbox:submit-button')
submit_button.click()

# Ждем когда залогинится и загрузит страницу
time.sleep(3)

# находим первое письмо, открываем его и ждем загрузки
first_mail = driver.find_element_by_class_name('llc')
first_mail_link = first_mail.get_attribute('href')
driver.get(first_mail_link)
time.sleep(2)

# константы для обработки даты
MONTHS = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
          'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
DAYS_REL = {'Вчера': dt.today() - td(days=1),
            'Сегодня': dt.today()}

while True:
    # ждем полной загрузки страницы с письмом
    # try:
    #    mail = WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    # except NoSuchElementException as e:
    #    break
    # ожидаем (без нее не работает на быстрых письмах, mail.ru как будто обрубает активность)
    time.sleep(0.4)
    # вытаскиваем инфу из письма
    mail_from = driver.find_element_by_class_name('letter-contact').get_attribute('title')
    mail_subj = driver.find_element_by_class_name('thread__subject').text
    mail_text = driver.find_element_by_class_name('letter__body').text
    mail_date = driver.find_element_by_class_name('letter__date').text
    # Преобразовываем дату в datatime format
    # варианты даты "7 декабря 2019, 11:32", "7 декабря, 11:32", "Вчера, 11:32", "Сегодня, 11:32"
    day_str, month_str, year_str = None, None, None
    try:
        parts = mail_date.split(' ')
        time_str = parts[-1]
        if len(parts) == 4:
            year_str = parts[2].replace(',', '')
            month_str = MONTHS[parts[1]]
            day_str = parts[0]
        elif len(parts) == 3:
            year_str = str(dt.today().year)
            month_str = MONTHS[parts[1].replace(',', '')]
            day_str = parts[0]
        elif len(parts) == 2:
            day_rel = parts[0].replace(',', '')
            year_str = str(DAYS_REL[day_rel].year)
            month_str = str(DAYS_REL[day_rel].month)
            day_str = str(DAYS_REL[day_rel].day)
        t_date = dt.strptime(f'{day_str} {month_str} {year_str}, {time_str}', '%d %m %Y, %H:%M')
    except (ValueError, IndexError):
        t_date = None

    # Сохраняем инфу в базу
    mails.insert_one({'from':   mail_from,  # адрес from
                      'subj':   mail_subj,  # тема письма
                      'text':   mail_text,  # текст письма
                      's_date': mail_date,  # дата из источника, в строковом формате
                      't_date': t_date      # дата преобразолванная в datatime формат
                      })
    # Проверяем статус кнопки "Следующее"
    # если активна - переходим к следующему письму
    # иначе - выходим из обработки
    down_button = driver.find_element_by_xpath('//span[@data-title="Следующее" or @title = "Следующее"]')
    if not down_button.get_attribute('disabled'):
        down_button.click()
    else:
        break
