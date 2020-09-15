from pymongo import MongoClient
from pprint import pprint
import shutil
import pandas as pd
import json


hh = pd.read_csv('hh_ru.csv', index_col='Unnamed: 0')
sj = pd.read_csv('superjob_ru.csv', index_col='Unnamed: 0')


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


db_name = 'bd_vacancy'
col_name = 'vacancy'
#save_all_mongodb(db_name, hh, col_name)
#save_all_mongodb(db_name, sj, col_name)

print(read_df_mongodb(db_name, col_name, {'$or':[ {'proposal_max': {'$gt': 100000}}, {'proposal_min': {'$gt': 100000}}]}))

sj = sj.append(pd.DataFrame([['https://www.test4.ru', 'test4', 'test4', 110000.0, 110000.0, 'руб.']], columns = ['link', 'name', 'main_link', 'proposal_min', 'proposal_max', 'proposal_currency']), ignore_index=True)
print('-------------------------------------------------------------------')
add_new_mongodb(db_name, sj, 'link', col_name)

#print_all_bd_mongodb(bd_name)
#drop_collection_mongodb(db_name, col_name)

df = read_df_mongodb(db_name, col_name, {'$or':[ {'proposal_max': {'$gt': 100000}}, {'proposal_min': {'$gt': 100000}}]})

print(df)
print(df.info())
#print_all_bd_mongodb(db_name, col_name)

