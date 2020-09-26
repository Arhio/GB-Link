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

driver.get('https://account.mail.ru/login/')

elem = driver.find_element_by_xpath("//input[@name='username']")
elem.send_keys('arhio1984@mail.ru')
elem.send_keys(Keys.ENTER)
elem = driver.find_element_by_xpath("//input[@name='password']")
elem.send_keys('NextPassword172')
elem.submit()
b = 0
try:
    b = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='dataset__items']")))
finally:
    pass
    #driver.quit()

elem = driver.find_elements_by_xpath("//div[@class='dataset__items']//a")
list_link = []

for a in elem:
    link = a.get_attribute('href')
    if 'https://e.mail.ru/inbox' in str(link):
        list_link.append(a.get_attribute('href'))

mails = pd.DataFrame()
idx = -1

for link in list_link:
    idx += 1
    driver.get(link)
    try:
        b = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='letter-body']")))
    finally:
        pass
        # driver.quit()
    subject = driver.find_element_by_xpath("//h2[@class='thread__subject']").text
    mails.loc[idx, 'subject'] = subject
    mails.loc[idx, 'date'] = driver.find_element_by_xpath("//div[@class='letter__date']").text
    mails.loc[idx, 'created_at'] = datetime.now()
    from_ = driver.find_element_by_xpath("//span[@class='letter-contact']").text
    mails.loc[idx, 'letter-contact'] = from_
    mails.loc[idx, 'recipients'] = driver.find_element_by_xpath("//div[@class='letter__recipients letter__recipients_short']").text
    body = driver.find_element_by_xpath("//div[@class='letter-body']").text
    mails.loc[idx, 'body'] = body
    mails.loc[idx, 'hash_mail'] = hash(from_ + subject + body)


db_name = 'db_mails'
col_name = 'mails'
add_new_mongodb(db_name, mails, 'hash_mail', col_name)
print_all_bd_mongodb(db_name, col_name)
driver.quit()
