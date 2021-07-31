""" 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json."""
import requests
import json

URL = 'https://api.github.com/'
name = 'den41apple'  # Имя пользователя
node = f'users/{name}/repos'
response = requests.get(url=URL + node,
                        headers={'Accept': 'application/vnd.github.v3+json'})
response = response.json()

with open('response.json', 'w') as file:
    json.dump(response, file)

for el in response:
    print(el['name'])
