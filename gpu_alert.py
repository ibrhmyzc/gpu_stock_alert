import requests
from bs4 import BeautifulSoup
import time
import winsound
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from multiprocessing import Pool
import re

options = Options()
# options.headless = True
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")

duration = 1000
freq = 800
list_add_to_cart = "data-add-to-cart"
grid_add_to_cart = "data-grid-add-to-cart"
class_add_to_cart = "a-button-stack"


wishlist_tr = 'https://www.amazon.com.tr/hz/wishlist/genericItemsPage/3BVI6714JE7Z9?type=wishlist&_encoding=UTF8'
wishlist_uk = 'https://www.amazon.co.uk/hz/wishlist/ls/1O1ZOBALWLKQP/ref=nav_wishlist_lists_1?_encoding=UTF8&type=wishlist'
wishlist_de = 'https://www.amazon.de/hz/wishlist/genericItemsPage/7BJVUHN6LXTY?type=wishlist&_encoding=UTF8'
wishlist_fr = 'add your own PUBLIC wishlist'
wishlist_it = 'add your own PUBLIC wishlist'
wishlist_es = 'add your own PUBLIC wishlist'
wishlist_us = "https://www.amazon.com/hz/wishlist/ls/23YX14E1GPU2B/ref=nav_wishlist_lists_2?_encoding=UTF8&type=wishlist"


regions = {
    'TR': [wishlist_tr],
    'UK': [wishlist_uk],
    'DE': [wishlist_de],
    'FR': [wishlist_fr],
    'IT': [wishlist_it],
    'ES': [wishlist_es],
    'US': [wishlist_us]
}


default_price = 9999
price_map = {
    'TR': {
        '3060': 6500,
        '3070': 9000,
        '3080': 12000,
        '3090': 20000
    },
    'UK': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    },
    'DE': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    },
    'ES': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    },
    'IT': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    },
    'FR': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    },
    'US': {
        '3060': 600,
        '3070': 900,
        '3080': 1100,
        '3090': 2000
    }
}


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "cache-control": "nocache",
    "pragma": "no-cache",
    "referer": 'www.amazon.de',
}


def check_amazon(region):
    browser = webdriver.Chrome(
        ChromeDriverManager().install(),  chrome_options=options)
    print("initialized for {}".format(region))
    while True:
        try:
            check_for_wishlist(browser, region)
        except Exception as e:
            print("ERROR M: {}".format(e))


def check_for_wishlist(browser, region):
    urls = regions[region]
    for url in urls:
        browser.get(url)
        pagedown(browser.find_element_by_tag_name("body"))
        is_grid_view = browser.find_elements_by_id("g-items-grid") != []
        if is_grid_view:
            list_view_button = browser.find_elements_by_id('list-view-switcher')
            ActionChains(browser).click(list_view_button).perform()
        for gpu in get_gpus(browser):
            if is_button_active(gpu):
                check_gpu(gpu, region)


def is_button_active(gpu):
    button = gpu.find_element_by_class_name(class_add_to_cart).find_element_by_tag_name('span')
    return button.get_attribute(grid_add_to_cart) != None or button.get_attribute(list_add_to_cart) != None


def pagedown(elem):
    no_of_pagedowns = 2
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
        no_of_pagedowns -= 1


def get_gpus(browser):
    is_grid_view = browser.find_elements_by_id("g-items-grid") != []
    if(is_grid_view):
        return browser.find_elements_by_id("g-items-grid")[0].find_elements_by_tag_name("li")
    else:
        return browser.find_elements_by_id("g-items")[0].find_elements_by_tag_name("li")


def check_gpu(gpu, region):
    try:
        brand = gpu.find_element_by_tag_name(
            "h3").find_element_by_tag_name("a").get_attribute("title")
        product_link = gpu.find_element_by_tag_name(
            "h3").find_element_by_tag_name("a").get_attribute("href")
        product_response = requests.get(product_link, headers=headers)
        product_page = BeautifulSoup(product_response.content, "html.parser")
        seller = product_page.find("a", id='sellerProfileTriggerId').text if product_page.find("a", id='sellerProfileTriggerId') != None else (
            product_page.find("span", class_="tabular-buybox-text").text if product_page.find("span", class_="tabular-buybox-text") != None else "")
        try:
            price = gpu.find_element_by_class_name("a-price").text
        except:
            price = "price error"
        stock_date = datetime.datetime.now()
        print('STOCK FOUND IN AMAZON {} - {} - {} -  from {} - at {}:{}'.format(region,
                                                                                price, brand, seller, stock_date.hour, stock_date.minute))
        if cast_price_to_double(price) <= get_max_price(region, brand.lower()):
            winsound.Beep(freq, duration)
    except Exception as e:
        print("ERROR P: {}".format(e))


def cast_price_to_double(price):
    return float(re.sub('[^0-9]', '', price)) // 100


def get_gpu_brand(brand):
    if brand.find('3060') != -1:
        return '3060'
    elif brand.find('3070') != -1:
        return '3070'
    elif brand.find('3080') != -1:
        return '3080'
    elif brand.find('3090') != -1:
        return '3090'
    return ''


def get_max_price(region, brand):
    key_brand = get_gpu_brand(brand)
    return price_map[region][key_brand] if key_brand in price_map[region] else default_price


if __name__ == '__main__':
    pool = Pool()
    # input_regions = ['TR']
    input_regions = ['TR', 'DE', 'UK', 'US']
    pool.map(check_amazon, input_regions)
