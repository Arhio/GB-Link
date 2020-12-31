from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')


driver = webdriver.Chrome('/usr/local/bin/chromedriver',options=chrome_options)
driver.get('https://pikabu.ru/')

for i in range(5):
    time.sleep(5)
    articles = driver.find_elements_by_tag_name('article')
    action = ActionChains(driver)
    action.move_to_element(articles[-1])
    action.perform()