from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pprint import pprint
import time

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

products = []
driver.get('https://www.mvideo.ru')
time.sleep(2)

actions = ActionChains(driver)
actions.move_by_offset(200, 200).click()
actions.perform()
time.sleep(1)

new_products_block = driver.find_element_by_xpath("//h2[contains(text(), 'Новинки')]/../../following-sibling::div")
time.sleep(0.5)
page_scroll = ActionChains(driver)
page_scroll.move_to_element(new_products_block).perform()
time.sleep(1)

next_btn = new_products_block.find_element_by_xpath(".//a[contains(@class, 'next-btn')]")
cls_next_btn = next_btn.get_attribute('class')
while cls_next_btn == 'next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right':
    time.sleep(0.5)
    next_btn = new_products_block.find_element_by_xpath(".//a[contains(@class, 'next-btn')]")
    cls_next_btn = next_btn.get_attribute('class')
    time.sleep(0.5)
    next_btn.click()
product_items = new_products_block.find_elements_by_xpath(".//a[contains(@class, 'fl-product-tile-title__link')]")
price_items = new_products_block.find_elements_by_xpath(".//span[@itemprop='price']")


index = 0
for item in product_items:
    product_dict = {}
    title = item.get_attribute('text').replace('\n', '').split()
    product_dict['title'] = ' '.join(title)
    product_dict['link'] = item.get_attribute('href')
    products.append(product_dict)


def write_db(ip, port, db_name, collection_name, data):
    mongodb = MongoClient(ip, port)
    db = mongodb[db_name]
    collection = db[collection_name]
    for el in data:
        collection.update_one({'link': el['link']}, {'$set': el}, upsert=True)


write_db('localhost', 27017, 'mvidio', 'new_products', products)
pprint(products)