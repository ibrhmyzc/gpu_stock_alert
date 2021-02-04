import requests
from bs4 import BeautifulSoup
import time
import winsound
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import datetime
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import re

options = Options()
options.headless = True
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "cache-control": "nocache",
    "pragma": "no-cache",
    "referer": 'www.amazon.de',
}

duration = 1000
freq = 800

url_tr = 'add your own PUBLIC wishlist amazon.com.tr'
key_tr = 'Sepete Ekle'
url_de = 'add your own PUBLIC wishlist amazon.de'
key_de = 'In den Einkaufswagen'
url_uk = 'add your own PUBLIC wishlist amazon.co.uk'
key_uk = 'Add to Basket'
url_fr = 'add your own PUBLIC wishlist'
key_fr = 'Ajouter au panier'
url_it = 'add your own PUBLIC wishlist'
key_it = 'Aggiungi al carrello'
url_es = 'add your own PUBLIC wishlist'
key_es = 'Añadir a la cesta'

regions = {
    'TR': {
        'url': url_tr,
        'key': key_tr
    },
    'UK': {
        'url': url_uk,
        'key': key_uk
    },
    'DE': {
        'url': url_de,
        'key': key_de
    },
    'FR': {
        'url': url_fr,
        'key': key_fr
    },
    'IT': {
        'url': url_it,
        'key': key_it
    },
    'ES': {
        'url': url_es,
        'key': key_es
    }
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
    }
}


def check_amazon(region):
    browser = webdriver.Chrome(
        ChromeDriverManager().install(),  chrome_options=options)
    print("initialized for {}".format(region))
    while True:
        try:
            time.sleep(1)
            check_for_wishlist(browser, region)
        except Exception as e:
            print("ERROR M: {}".format(e))


def check_for_wishlist(browser, region):
    url = regions[region]['url']
    key = regions[region]['key']
    browser.get(url)
    pagedown(browser.find_element_by_tag_name("body"))
    for gpu in get_gpus(browser):
        if str(gpu.text).find(key) != -1:
            check_gpu(gpu, region)


def pagedown(elem):
    no_of_pagedowns = 3
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        no_of_pagedowns -= 1


def get_gpus(browser):
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
    input_regions = ['TR']
    # input_regions = ['TR', 'DE', 'UK']
    pool.map(check_amazon, input_regions)
