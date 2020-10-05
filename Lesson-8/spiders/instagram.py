# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from items import InstaparserItem, InstFollowByItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    #атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = '89880058491'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1601831038:AaVQAKKdiZnLMBKPnSNSTdsV9+Mnd6sHhsa927AgtAD+j9o60+i7PZgLxPnsTbYleAijtu+5TJIzNivYJsNQdX/y2e5WBqOeiaOKbHlgFyjLAYGxgRPg1/ChXQmCTWv+983DjDKRa14tzFiuXOSaZQ=='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['ai_machine_learning', 'monetochkaliska']      #Пользователь, у которого собираем посты. Можно указать список
    # 'unsupervisedlearning', 'reinforcementlearning',
    dict_post_hash =           {'ai_machine_learning':'56a7068fea504063273cc2120ffd54f3', 'monetochkaliska':'56a7068fea504063273cc2120ffd54f3'} #hash для получения данных по постах с главной страницы

    dict_user_subscriptions  = {'ai_machine_learning':'d04b0a864b4b54837c0d870b0e77e076', 'monetochkaliska':'d04b0a864b4b54837c0d870b0e77e076'}
    dict_user_id_subscriptions = {'ai_machine_learning': '7709057810', 'monetochkaliska': '2964153030'}
    dict_subscriptions =       {'ai_machine_learning':'c76146de99bb02f6415203be841dd25a', 'monetochkaliska':'c76146de99bb02f6415203be841dd25a'}

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'     #hash для получения данных по постах с главной страницы

    def parse(self, response:HtmlResponse):             #Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)   #csrf token забираем из html
        yield scrapy.FormRequest(                   #заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username':self.insta_login, 'enc_password':self.insta_pwd},
            headers={'X-CSRFToken':csrf_token}
        )

    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:                 #Проверяем ответ после авторизации
            if len(self.parse_users) > 0:
                for user in self.parse_users:
                    yield response.follow(                  #Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                        f'/{user}',
                        callback= self.user_data_parse,
                        cb_kwargs={'username':user}
                    )

    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)       #Получаем id пользователя


        variables_user_subs= {
            "id":self.dict_user_id_subscriptions[username],
            "include_reel":True,
            "fetch_mutual":False,
            "first":12
        }
        url_user_subscriptions = f'{self.graphql_url}query_hash={self.dict_subscriptions[username]}&{urlencode(variables_user_subs)}'
        yield response.follow(
            url_user_subscriptions,
            callback=self.user_subscriptions_parser,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_user_subs)}
        )


        variables_subs= {
            "id":self.dict_user_id_subscriptions[username],
            "include_reel": True,
            "fetch_mutual": False,
            "first": 12
        }
        url_subscriptions = f'{self.graphql_url}query_hash={self.dict_user_subscriptions[username]}&{urlencode(variables_subs)}'
        yield response.follow(
            url_subscriptions,
            callback=self.user_subscriptions_user_parser,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_subs)}
        )


        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        url_posts = f'{self.graphql_url}query_hash={self.dict_post_hash[username]}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username':username,
                       'user_id':user_id,
                       'variables':deepcopy(variables)}         #variables ч/з deepcopy во избежание гонок
        )


    def user_subscriptions_parser(self, response:HtmlResponse, username,user_id,variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.dict_subscriptions[username]}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_subscriptions_parser,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        follows = j_data.get('data').get('user').get('edge_followed_by').get('edges') #Сами подписчики
        for follow in follows:                                                        #Перебираем посты, собираем данные
            item = InstFollowByItem(
                user_id = follow['node']['id'],
                id = user_id,
                name = follow['node']['username'],
                full_name = follow['node']['full_name'],
                pic_url = follow['node']['profile_pic_url'],
                is_private = follow['node']['is_private'],
                is_verified = follow['node']['is_verified'],
                followed_by_viewer = follow['node']['followed_by_viewer'],
                requested_by_viewer = follow['node']['requested_by_viewer'],
                post = follow['node']
            )
        yield item #В пайплайн


    def user_subscriptions_user_parser(self, response:HtmlResponse, username,user_id,variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.dict_user_subscriptions[username]}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_subscriptions_user_parser,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        follows = j_data.get('data').get('user').get('edge_follow').get('edges') #Сами подписчики
        for follow in follows:                                                   #Перебираем посты, собираем данные
            item = InstFollowByItem(
                user_id = user_id,
                id = follow['node']['id'],
                name = follow['node']['username'],
                full_name = follow['node']['full_name'],
                pic_url = follow['node']['profile_pic_url'],
                is_private = follow['node']['is_private'],
                is_verified = follow['node']['is_verified'],
                followed_by_viewer = follow['node']['followed_by_viewer'],
                requested_by_viewer = follow['node']['requested_by_viewer'],
                post = follow['node']
            )
        yield item #В пайплайн


    def user_posts_parse(self, response:HtmlResponse,username,user_id,variables):   #Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):                                          #Если есть следующая страница
            variables['after'] = page_info['end_cursor']                            #Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')     #Сами посты
        for post in posts:                                                                      #Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id = user_id,
                photo = post['node']['display_url'],
                likes = post['node']['edge_media_preview_like']['count'],
                post = post['node']
            )
        yield item                  #В пайплайн


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