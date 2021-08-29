import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instagram.items import InstagramItem
from urllib.parse import urlencode
from copy import deepcopy


class InstagramcomSpider(scrapy.Spider):

    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'Onliskill_udm'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1629825416:ASpQAMvl1EAdo0NdRZNcM1/pjlU9rRg4n4cjCM00SDGSV5pDN6XbC93ZbYN67HUOHkXZnGGe2gIWPU2qtQY0HAkIjR5U5syu+lv8qtqeI7cyy2ua6WmBV6AngVo1apn3eJ6O3UAFVgb+q5HtHsQ='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    graphql_url = 'https://www.instagram.com/graphql/query/?'

    subscribers_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def __init__(self, users_list):
        self.parse_users = users_list      

    def parse(self, response: HtmlResponse):  
        csrf_token = self.fetch_csrf_token(response.text)   
        yield scrapy.FormRequest(                   
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:                 
            for user in self.parse_users:
                yield response.follow(                 
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       
        variables={'id': user_id,                                    
                   'username': username,
                   'first': 12}                                      

        url_subscribers = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_subscribers,
            callback=self.subscribers_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       }
        )

        url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'
        yield response.follow(
            url_subscriptions,
            callback=self.subscriptions_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       }

        )

    def subscribers_parse(self, response, user_id, username, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_subscribers = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'

            yield response.follow(
                url_subscribers,
                callback=self.subscribers_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )

        subscribers = j_body.get('data').get('user').get('edge_followed_by').get('edges')
        for subscriber in subscribers:
            item = InstagramItem(
                source_id=user_id,
                source_name=username,
                user_id=subscriber['node']['id'],
                user_name=subscriber['node']['username'],
                user_fullname=subscriber['node']['full_name'],
                photo_url=subscriber['node']['profile_pic_url'],
                subs_type='subscriber'
            )

            yield item

    def subscriptions_parse(self, response, user_id, username, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_follow').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'

            yield response.follow(
                url_subscriptions,
                callback=self.subscriptions_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )

        subscriptions = j_body.get('data').get('user').get('edge_follow').get('edges')
        for subscription in subscriptions:
            item = InstagramItem(
                source_id=user_id,
                source_name=username,
                user_id=subscription['node']['id'],
                user_name=subscription['node']['username'],
                user_fullname=subscription['node']['full_name'],
                photo_url=subscription['node']['profile_pic_url'],
                subs_type='subscription'
            )

            yield item

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
