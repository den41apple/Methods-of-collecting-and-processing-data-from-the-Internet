"""2. (По желанию/возможности)Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
Ответ сервера записать в файл.
Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны."""

import json
import requests

TOKEN = ''  # Необходимо вставить токен для работы
if TOKEN == '':
    TOKEN = input('Для получения информации вставьте токен сюда: ')
address = 'https://api.vk.com/method/'
version = '5.131'
method = 'groups.get'
account_id = 'den41'  # Название страницы или id аккаунта
# Вызов 1-го метода для получения всех id групп
response = requests.get(address + method,
                        params={
                            'access_token': TOKEN,
                            'v': version,
                            'account_id': account_id,

                        })
response = json.loads(response.text)['response']
# Вызов 2-го метода для получения информации о всех группах с помощью id полученных ранее
method = 'groups.getById'  # Переопределяем метод
ids = ','.join(map(str, response['items']))  # Передаем id полученные от первого метода
response_2 = requests.get(address + method,
                          params={
                              'access_token': TOKEN,
                              'v': version,
                              'account_id': account_id,
                              'group_ids': ids

                          })
response_2 = json.loads(response_2.text)['response']

print('Список сообществ:')
for group in response_2:
    print(group['name'])