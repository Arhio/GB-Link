import shutil
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

#https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&resume=dcd75cc1ff05871f780039ed1f304f6e795167&text=Data&page=2
#https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text=Data

idx = 0

word = 'data scientist'


main_link = 'https://www.superjob.ru'
params = {
          'geo[t][0]': '4',
          'keywords': word,

          'page':'0'
          }
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.86 YaBrowser/20.8.0.864 (beta) Yowser/2.5 Safari/537.36'}



html = requests.get(main_link + '/vakansii/stazher.html', params=params, headers=headers)

soup = bs(html.text, 'html.parser')

pagenation = soup.find('div', {'class':'_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo'})
pag = soup.find_all('span', {'class':'qTHqo _1mEoj _2h9me DYJ1Y _2FQ5q _2GT-y'})
idx_pos = 0

maxpos = 1
for page in pag:
    txt = page.find('span', {'class':'_3IDf-'})
    if txt:
        txt = txt.getText()
        if txt.isdigit():
            pos = int(txt)
            if maxpos < (pos):
                maxpos = pos


jobs = pd.DataFrame()

while idx < maxpos:

    job_block = soup.find('div',{'class':'_1Ttd8 _2CsQi'})
    job_list = job_block.find_all('div',{'class':'jNMYr GPKTZ _1tH7S'})



    for serial in job_list:
        idx_pos += 1
        serial_data = {}

        serial_info = serial.find('a', {'class':'icMQ_'})
        jobs.loc[idx_pos, 'link'] = serial_info['href']
        jobs.loc[idx_pos, 'name'] = serial_info.getText()
        jobs.loc[idx_pos, 'main_link'] = main_link
        serial_proposal = serial.find('span', {'class':'_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'})
        if serial_proposal:
            s = serial_proposal.getText().lower().replace(f'\xa00', f'0').replace(f'\xa0—\xa0', f'-').replace(f'\xa0', f' ').split(' ')

            if s[0] == 'от':
                jobs.loc[idx_pos, 'proposal_min'] = s[1]
                jobs.loc[idx_pos, 'proposal_currency'] = s[2]
            elif s[0] == 'до':
                jobs.loc[idx_pos, 'proposal_max'] = s[1]
                jobs.loc[idx_pos, 'proposal_currency'] = s[2]

            elif s[0].find('-') == -1:
                jobs.loc[idx_pos, 'proposal_min'] = s[0]
                jobs.loc[idx_pos, 'proposal_currency'] = s[1]
            else:
                jobs.loc[idx_pos, 'proposal_min'], jobs.loc[idx_pos, 'proposal_max'] = s[0].split('-')

                jobs.loc[idx_pos, 'proposal_currency'] = s[1]

    print(idx)
    idx += 1

    params = {
                'geo[t][0]': '4',
                'keywords': word,
                'page': idx
            }
    html = requests.get(main_link + '/vakansii/stazher.html', params=params, headers=headers)
    soup = bs(html.text, 'html.parser')

print(type(jobs.info()))
jobs.to_csv('superjob_ru.csv')

