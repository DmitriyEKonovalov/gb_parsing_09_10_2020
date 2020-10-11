"""
2.
Изучить список открытых API (https://www.programmableweb.com/category/all/apis). 
Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. 
Ответ сервера записать в файл.
Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide). 
Сделайте запрос, чтб получить список всех сообществ на которые вы подписаны.

"""

import requests

# insert own params
access_token = '######'
user_id = '#####'

main_link = 'https://api.vk.com/method/'
method = 'groups.get'
params = {
    'user_id': user_id,
    'extended': '1',
    'count': '1000',
    'access_token': access_token,
    'v': '5.124'
    }

response = requests.get(main_link + method, params=params).json()

with open('hw01_02out.txt', 'w', encoding='utf8') as f_out:
    f_out.writelines([str(i['name']) + '\n' for i in response['response']['items']])
