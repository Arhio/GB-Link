from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import shutil
import requests
from pprint import pprint
from pymongo import MongoClient
import pandas as pd
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


options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')

driver.get('https://www.mvideo.ru/')

try:
    b = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='accessories-carousel-wrapper']//a[@class='next-btn sel-hits-button-next']"))).click()
finally:
    pass

driver.execute_script(f"window.scrollTo(0, ({3.5} * document.body.scrollHeight / {15}))")

while True:
    try:
        b = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                        "//div[contains(text(), 'Хиты продаж')]/../../..//a[@class='next-btn sel-hits-button-next']")))
        elem = driver.find_element_by_xpath(
            "//div[contains(text(), 'Хиты продаж')]/../../..//a[@class='next-btn sel-hits-button-next']")
        elem.click()
    except:
        break

elems = driver.find_elements_by_xpath("//div[contains(text(), 'Хиты продаж')]/../../..//li")

items = pd.DataFrame()
idx = -1
for el in elems:
    idx += 1
    items.loc[idx, 'main_link'] = 'https://www.mvideo.ru/'
    items.loc[idx, 'title'] = el.find_element_by_xpath('.//a[@class="sel-product-tile-title"]').get_attribute('data-track-label')
    items.loc[idx, 'link'] = el.find_element_by_xpath('.//a[@class="sel-product-tile-title"]').get_attribute('href')
    info = el.find_element_by_xpath('.//a[@class="sel-product-tile-title"]').get_attribute('data-product-info')
    items.loc[idx, 'info'] = info
    items.loc[idx, 'reviews_quantity'] = el.find_element_by_xpath('.//span[@class="c-star-rating_reviews-qty"]').text
    items.loc[idx, 'reviews_procent'] = el.find_element_by_xpath('.//span[@class="c-star-rating__stars c-star-rating__stars_active font-icon icon-star"]').get_attribute('style')
    items.loc[idx, 'created_at'] = datetime.now()
    items.loc[idx, 'hash'] = hash(info)


db_name = 'db_offers'
col_name = 'offers'
add_new_mongodb(db_name, items, 'hash', col_name)
print_all_bd_mongodb(db_name, col_name)
driver.quit()


