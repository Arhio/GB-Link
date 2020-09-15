import shutil
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

#https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&resume=dcd75cc1ff05871f780039ed1f304f6e795167&text=Data&page=2
#https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=Data

idx = 0

word = 'data scientist'

main_link = 'https://hh.ru'
params = {'area': '1',
          'fromSearchLine': 'true',
          'st': 'searchVacancy',
          'text': word,
          'page':'0'
          }
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.86 YaBrowser/20.8.0.864 (beta) Yowser/2.5 Safari/537.36'}


html = requests.get(main_link + '/search/vacancy', params=params, headers=headers)

soup = bs(html.text, 'html.parser')

pagenation = soup.find_all('a', {'class':'bloko-button HH-Pager-Control'})

idx_pos = 0

maxpos = 1
for page in pagenation:
    pos = int(page.getText())
    if maxpos < (pos):
        maxpos = pos

jobs = pd.DataFrame()

while idx < maxpos:
    job_block = soup.find('div',{'class':'vacancy-serp'})
    job_list = job_block.find_all('div',{'class':'vacancy-serp-item'})


    for serial in job_list:
        idx_pos += 1
        serial_data = {}
        serial_info = serial.find('a')
        jobs.loc[idx_pos, 'link'] = str(serial_info['href'])
        jobs.loc[idx_pos, 'name'] = str(serial_info.getText())
        jobs.loc[idx_pos, 'main_link'] = str(main_link)
        serial_side = serial.find('div', {'class':'vacancy-serp-item__sidebar'})
        serial_proposal = serial_side.find('span', {'class':'bloko-section-header-3'})
        if serial_proposal:
            s = serial_proposal.getText().lower().split(' ')
            if s[0] == 'от':
                jobs.loc[idx_pos, 'proposal_min'] = int(s[1].replace(f'\xa0', f''))
                jobs.loc[idx_pos, 'proposal_currency'] = str(s[2])
            elif s[0] == 'до':
                jobs.loc[idx_pos, 'proposal_max'] = int(s[1].replace(f'\xa0', f''))
                jobs.loc[idx_pos, 'proposal_currency'] = str(s[2])
            else:
                a, b = s[0].replace(f'\xa0', f'').split('-')
                jobs.loc[idx_pos, 'proposal_min'] = int(a)
                jobs.loc[idx_pos, 'proposal_max'] = int(b)
                jobs.loc[idx_pos, 'proposal_currency'] = str(s[1])

    print(idx)
    idx += 1
    params = {'area': '1',
                  'fromSearchLine': 'true',
                  'st': 'searchVacancy',
                  'text': word,
                  'page': idx
                  }
    html = requests.get(main_link + '/search/vacancy', params=params, headers=headers)
    soup = bs(html.text, 'html.parser')

print(type(jobs.info()))
jobs.to_csv('hh_ru.csv')