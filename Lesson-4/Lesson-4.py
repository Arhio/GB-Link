from pymongo import MongoClient
from pprint import pprint
import shutil
import pandas as pd
import requests
import json
from lxml import html
from datetime import datetime, date, time, timedelta
import time as tm


def _connect_mongo(host, port, username, password, db):
    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)
    return conn[db]


def save_all_mongodb(db, df, collection, host='127.0.0.1', port=27017, username=None, password=None):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    records = json.loads(df.T.to_json()).values()
    db_collection = client[collection]
    db_collection.insert_many(records)

def drop_collection_mongodb(db, collection, host='127.0.0.1', port=27017, username=None, password=None):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    db_collection = client[collection]
    db_collection.drop()

def print_all_bd_mongodb(db, collection, host='127.0.0.1', port=27017, username=None, password=None):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    db_collection = client[collection]
    for e in db_collection.find():
         pprint(e)

def print_find_mongodb(db, collection, query={}, host='localhost', port=27017, username=None, password=None):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    db_collection = client[collection]
    for e in db_collection.find(query):
         pprint(e)

def add_new_mongodb(db, df, name_field_id, collection, host='127.0.0.1', port=27017, username=None, password=None):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    db_collection = client[collection]
    records = json.loads(df.T.to_json()).values()
    for data in records:
        data_field_id = data[name_field_id]
        db_collection.update_one({name_field_id: data_field_id}, {'$set': data}, upsert=True)

def read_df_mongodb(db, collection, query={}, host='127.0.0.1', port=27017, username=None, password=None, no_id=True):
    client = _connect_mongo(host=host, port=port, username=username, password=password, db=db)
    db_collection = client[collection]
    cursor = db_collection.find(query)
    df = pd.DataFrame(list(cursor))
    if no_id & ('_id' in list(df)):
        del df['_id']
    return df



main_link = 'https://lenta.ru'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.86 YaBrowser/20.8.0.864 (beta) Yowser/2.5 Safari/537.36'}

response = requests.get(f'{main_link}', params={}, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']/a | //section[@class='row b-top7-for-main js-top-seven']//div[@class='first-item']/h2/a")

all_news = pd.DataFrame()
idx = -1
for new in news:
    idx += 1
    name = new.xpath("./text()")
    all_news.loc[idx, 'name'] = name[0].replace('\xa0','') if len(name) > 0 else None

    _time = new.xpath("./time/@datetime")
    _time = datetime.strptime(_time[0][1:].replace(', ', ' ')
                                     .replace('января', 'January')
                                     .replace('февраля', 'February')
                                     .replace('марта', 'March')
                                     .replace('апреля', 'April')
                                     .replace('мая', 'May')
                                     .replace('июня', 'June')
                                     .replace('июля', 'July')
                                     .replace('августа', 'August')
                                     .replace('сентября', 'September')
                                     .replace('октября', 'October')
                                     .replace('ноября', 'November')
                                     .replace('декабря', 'December'), "%H:%M %d %B %Y") if len(_time) > 0 else None
    all_news.loc[idx, 'time'] = _time
    all_news.loc[idx, 'source'] = "Lenta.ru"
    link = new.xpath("./@ref")
    all_news.loc[idx, 'link'] = link[0] if len(link) > 0 else None
    all_news.loc[idx, 'main_link'] = main_link
    all_news.loc[idx, 'hash'] = hash(str(main_link) + str(name) + str(_time))



main_link = 'https://yandex.ru/news'
response = requests.get(f'{main_link}', params={}, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath("//article[contains(@class, 'mg-card news-card')]")

for new in news:
    idx += 1
    name = new.xpath(".//a[@class='news-card__link']//text()")
    all_news.loc[idx, 'name'] = name[0].replace('\xa0', '') if len(name) > 0 else None

    _time = new.xpath(".//span[@class='mg-card-source__time']//text()")
    _time = _time[0].split(' ') if len(_time) > 0 else None
    if _time is not None:
        if _time[0] == 'вчера':
            _new = datetime.today() - timedelta(days=1)
            t = _time[-1].split(':')
            _time = datetime(_new.year, _new.month, _new.day, int(t[0]), int(t[1]), 0)
        elif _time[0].isdigit():
            _new = datetime.today()
            t = _time[-1].split(':')
            month = _time[1].replace('января', '1')\
                .replace('февраля', '2')\
                .replace('марта', '3')\
                .replace('апреля', '4')\
                .replace('мая', '5')\
                .replace('июня', '6')\
                .replace('июля', '7')\
                .replace('августа', '8')\
                .replace('сентября', '9')\
                .replace('октября', '10')\
                .replace('ноября', '11')\
                .replace('декабря', '12')
            _time = datetime(_new.year, int(month), int(_time[0]), int(t[0]), int(t[1]), 0)
        else:
            _new = datetime.today()
            t = _time[0].split(':')
            _time = datetime(_new.year, _new.month, _new.day, int(t[0]), int(t[1]), 0)

    all_news.loc[idx, 'time'] = _time
    link = new.xpath(".//a[@class='news-card__link']/@ref")
    all_news.loc[idx, 'link'] = link[0] if len(link) > 0 else None
    source = new.xpath(".//span[@class='mg-card-source__source']/a//text()")
    all_news.loc[idx, 'source'] = source[0] if len(source) > 0 else None
    all_news.loc[idx, 'main_link'] = main_link
    all_news.loc[idx, 'hash'] = hash(str(main_link) + str(name) + str(_time))



main_link = 'https://news.mail.ru'
response = requests.get(f'{main_link}', params={}, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath("//div[contains(@class, 'daynews__item')] | //li[contains(@class, 'list__item')] | //div[contains(@class, 'newsitem n')]")

for new in news:
    news_link = new.xpath(".//a/@href")
    if len(news_link) > 0:
        idx += 1
        ispassed = False
        while ispassed is False:
            try:
                link_norm = news_link[0] if news_link[0][0:4] == 'http' else main_link + news_link[0]
                response_news = requests.get(f'{link_norm}', params={}, headers=headers)
                dom_news = html.fromstring(response_news.text)

                name = dom_news.xpath("//div[contains(@class,'hdr hdr_collapse')]//span//text()")
                all_news.loc[idx, 'name'] = name[0].replace('\xa0', '') if len(name) > 0 else None

                _time = dom_news.xpath("//span[contains(@class, 'breadcrumbs__item')]//span[contains(@class,'note__text breadcrumbs__text j')]/@datetime")
                _time = _time[0].split('+')[0] if len(_time) > 0 else None
                if (_time is not None):
                    _time = datetime.strptime(_time, "%Y-%m-%dT%H:%M:%S")
                all_news.loc[idx, 'time'] = _time

                all_news.loc[idx, 'link'] = link_norm
                source = dom_news.xpath("//span[contains(@class, 'breadcrumbs__item')]//a//text()")
                all_news.loc[idx, 'source'] = source[0] if len(source) > 0 else None
                all_news.loc[idx, 'main_link'] = main_link
                all_news.loc[idx, 'hash'] = hash(str(main_link) + str(name) + str(_time))
                tm.sleep(0.001)
                ispassed = True
            except:
                pass


db_name = 'db_news'
col_name = 'news'
add_new_mongodb(db_name, all_news, 'hash', col_name)
print_all_bd_mongodb(db_name, col_name)

