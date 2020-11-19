"""
1.
Посмотреть документацию к API GitHub,
разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""

import requests
import json

main_link = 'https://api.github.com/users/DmitriyEKonovalov/repos'
response = requests.get(main_link).json()
with open('hw01_01out.json', 'w') as f_out:
    json.dump(response, f_out)
