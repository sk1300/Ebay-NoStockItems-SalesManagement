#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""#Chromiumとseleniumをインストール
print("前処理を開始")
!apt-get update
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
!pip install selenium
"""


# In[2]:


"""
①各サイトでキーワード検索（ユーザー操作）
↓↓
②-1 検索にヒットした一覧画面のURLを引数にしてツールを呼び出す（大量出品）（ユーザー操作。厳密には当社システムによる呼び出し）
②-2 上記のうちの１商品のURLを引数にしてツールを呼び出す（個別出品）（ユーザー操作。厳密には当社システムによる呼び出し）
↓↓
③各商品ページの抽出処理
【抽出したい情報】
・出品タイトル
・画像
・価格
・在庫の有無
・商品情報や説明文
※価格の変動や在庫などの監視は結構です。
↓↓
④抽出した情報を翻訳
【補足】翻訳機能については、単体で翻訳機能のみでも利用したいので個別で処理を呼び出せるようにお願いします。
↓↓
⑤抽出した情報と翻訳した情報を同時保持したCSVファイルを出力する
"""


# In[3]:


from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import csv
import datetime #ログ用
import os
import lxml.html
import random
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import time
import urllib.parse
import warnings #ログ用


# In[4]:


#翻訳APIのURL
#足りなくなったら追加する

script_url_list_index = 0

script_url_list = [
    'https://script.google.com/macros/s/AKfycbztdWMbpDcNYYLZSzdrYH-untbHXiaHNrr2QpSTNz71jFJq8SFZmox5eAJ2lzu34KWW/exec',
    'https://script.google.com/macros/s/AKfycbxIxMPMFKHgfeYK_bh9xj-_nwRXnFpC_NUuvEOfMPPOx2jRPLzqoaStKC9Idg3rRnH0/exec'
]


# In[16]:


#chromeをheadlessモードで起動する
def start_chrome():
    #print(datetime.datetime.now(), 'start_chrome')

    # Chrome Optionsの設定
    #options = Options()
    #options.add_argument('--headless')                 # headlessモードを使用する
    #options.add_argument('--disable-gpu')              # headlessモードで暫定的に必要なフラグ(そのうち不要になる)
    #options.add_argument('--disable-extensions')       # すべての拡張機能を無効にする。ユーザースクリプトも無効にする
    #options.add_argument('--proxy-server="direct://"') # Proxy経由ではなく直接接続する
    #options.add_argument('--proxy-bypass-list=*')      # すべてのホスト名
    #options.add_argument('--start-maximized')          # 起動時にウィンドウを最大化する
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')                         
    options.add_argument('--disable-gpu')                      
    options.add_argument('--disable-extensions')               
    options.add_argument('--proxy-server="direct://"')         
    options.add_argument('--proxy-bypass-list=*')              
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--lang=ja')                          
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--log-level=3")
    #options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'eager'

    # Chrome DriverのPath
    # driver_path = f'{os.path.dirname(os.path.abspath(__file__))}/chromedriver.exe'
    # driver_path = f'{os.path.dirname(os.path.abspath(__file__))}/chromedriver'
    # driver_path = f'/usr/local/bin/chromedriver.exe'
    
    # print(f'driver_path: {driver_path}')
    print(f'os.path.dirname: {os.path.dirname(os.path.abspath(__file__))}')
    print(f'os.path.abspath: {os.path.abspath(__file__)}')

    # Chrome Driverを起動する
    # driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.implicitly_wait(10)

    return driver


# In[6]:


#chromeをheadlessモードで起動する
#google colaboratoryで実行する場合はこちらを使用する
def start_chrome_colab():
  #print(datetime.datetime.now(), 'start_chrome_colab')

  #---------------------------------------------------------------------------------------
  # 処理開始
  #---------------------------------------------------------------------------------------
  # ブラウザをheadlessモード実行
  #print("\nブラウザを設定")
  #options = webdriver.ChromeOptions()
  #options.add_argument('--headless')
  #options.add_argument('--no-sandbox')
  #options.add_argument('--disable-dev-shm-usage')
  #driver = webdriver.Chrome('chromedriver',options=options)
  #driver.implicitly_wait(10)

  options = webdriver.ChromeOptions()
  options.add_argument('--headless')                         
  options.add_argument('--disable-gpu')                      
  options.add_argument('--disable-extensions')               
  options.add_argument('--proxy-server="direct://"')         
  options.add_argument('--proxy-bypass-list=*')              
  options.add_argument('--blink-settings=imagesEnabled=false')
  options.add_argument('--lang=ja')                          
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument("--log-level=3")
  #options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')
  options.add_experimental_option("excludeSwitches", ["enable-automation"])
  options.add_experimental_option('useAutomationExtension', False)
  options.page_load_strategy = 'eager'
  driver = webdriver.Chrome('chromedriver',options=options)
  driver.implicitly_wait(10) #これがないとメルカリの検索ページがうまく取得できない

  return driver


# In[7]:


#chromeを停止する
def end_chrome(driver): 
    #print(datetime.datetime.now(), 'end_chrome')

    driver.close()
    driver.quit()


# In[8]:


#ヤフオクの商品ページをスクレイピングする
def scrape_yahoo_item(product_url, csv_path, image_path, max_images, driver):      
    #print(datetime.datetime.now(), 'scrape_yahoo_item')

    time.sleep(1)
    driver.get(product_url)
    
    #出品タイトル
    title = driver.find_element_by_xpath('//h1[@class="ProductTitle__text"]').get_attribute('textContent')
    
    #画像
    image_list = []
    #画像複数枚
    if len(driver.find_elements_by_xpath('//li[contains(@class, "ProductImage__thumbnail")]/a/img')) > 0:
        for element in driver.find_elements_by_xpath('//li[contains(@class, "ProductImage__thumbnail")]/a/img'):
            image_list.append(element.get_attribute("src"))
    #画像1枚
    elif len(driver.find_elements_by_xpath('//div[@class="ProductImage__inner"]/img')) > 0:
        for element in driver.find_elements_by_xpath('//div[@class="ProductImage__inner"]/img'):
            image_list.append(element.get_attribute('src'))

    #ディレクトリを作成
    product_url_split_list = product_url.split("/")
    dirname = product_url_split_list[len(product_url_split_list)-1]
    os.makedirs(image_path + '/yahoo/' + dirname, exist_ok=True)
    
    #画像を保存
    for index, image in enumerate(image_list):
      if index < max_images:
        image_split_list = image.split("/")
        filename = image_split_list[len(image_split_list)-1]
        r = requests.get(image).content
        with open(image_path + '/yahoo/' + dirname + '/' + filename ,mode='wb') as f: # wb でバイト型を書き込める
          f.write(r)

    #画像のリストを固定長に変換
    fixed_image_list = [''] * 10
    for i in range(0, len(image_list)):
      fixed_image_list[i] = image_list[i]
    
    #価格
    price = ''
    #即決価格を取得
    if len(driver.find_elements_by_xpath('//div[@class="Price Price--buynow"]//dd[@class="Price__value"]')) > 0:
      text = driver.find_element_by_xpath('//div[@class="Price Price--buynow"]//dd[@class="Price__value"]').get_attribute('textContent')
      text = re.sub('\s', '', text)
      text = re.sub('円.*', '', text)
      text = re.sub('\D', '', text)
      price = text
    
    #在庫の有無
    stock = 'in_stock'
    #stock = 'out_of_stock'
    
    #商品情報や説明文
    explanation = driver.find_element_by_xpath('//div[@class="ProductExplanation__commentBody js-disabledContextMenu"]').text
    
    #ディレクトリを作成
    os.makedirs(csv_path, exist_ok=True)

    #csvファイル出力
    with open(csv_path + '/' + 'product_item.csv', 'a', encoding='utf8') as f:
        writer = csv.writer(
            f,
            delimiter=',',  # 区切り文字はカンマ
            quotechar='"',  # 囲い文字はダブルクォーテーション
            quoting=csv.QUOTE_NONNUMERIC    # 全ての非数値フィールドをクオート
        )

        writer.writerow([
          product_url,
          dirname,
          title,
          fixed_image_list[0],
          fixed_image_list[1],
          fixed_image_list[2],
          fixed_image_list[3],
          fixed_image_list[4],
          fixed_image_list[5],
          fixed_image_list[6],
          fixed_image_list[7],
          fixed_image_list[8],
          fixed_image_list[9],
          price,
          stock,
          explanation,
          translate(title),
          translate(explanation)
        ])


# In[9]:


#ヤフオクの商品ページをスクレイピングする
#requestsバージョン
def scrape_yahoo_item_requests(product_url, csv_path, image_path, max_images):      
    #print(datetime.datetime.now(), 'scrape_yahoo_item_requests')

    time.sleep(1)
    html = requests.get(product_url)
    soup = BeautifulSoup(html.text, 'html.parser')
    root = lxml.html.fromstring(str(soup))
    
    #出品タイトル
    title = root.xpath('//h1[@class="ProductTitle__text"]')[0].text_content()
    
    #画像
    image_list = []
    #画像複数枚
    if len(root.xpath('//li[contains(@class, "ProductImage__thumbnail")]/a/img')) > 0:
        for element in root.xpath('//li[contains(@class, "ProductImage__thumbnail")]/a/img'):
            image_list.append(element.attrib['src'])
    #画像1枚
    elif len(root.xpath('//div[@class="ProductImage__inner"]/img')) > 0:
        for element in root.xpath('//div[@class="ProductImage__inner"]/img'):
            image_list.append(element.attrib['src'])

    #ディレクトリを作成
    product_url_split_list = product_url.split("/")
    dirname = product_url_split_list[len(product_url_split_list)-1]
    os.makedirs(image_path + '/yahoo/' + dirname, exist_ok=True)
    
    #画像を保存
    for index, image in enumerate(image_list):
      if index < max_images:
        image_split_list = image.split("/")
        filename = image_split_list[len(image_split_list)-1]
        r = requests.get(image).content
        with open(image_path + '/yahoo/' + dirname + '/' + filename ,mode='wb') as f: # wb でバイト型を書き込める
          f.write(r)

    #画像のリストを固定長に変換
    fixed_image_list = [''] * 10
    for i in range(0, len(image_list)):
      fixed_image_list[i] = image_list[i]
    
    #価格
    price = ''
    #即決価格を取得
    if len(root.xpath('//div[@class="Price Price--buynow"]//dd[@class="Price__value"]')) > 0:
      text = root.xpath('//div[@class="Price Price--buynow"]//dd[@class="Price__value"]')[0].text_content()
      text = re.sub('\s', '', text)
      text = re.sub('円.*', '', text)
      text = re.sub('\D', '', text)
      price = text
    
    #在庫の有無
    stock = 'in_stock'
    #stock = 'out_of_stock'
    
    #商品情報や説明文
    explanation = root.xpath('//div[@class="ProductExplanation__commentBody js-disabledContextMenu"]')[0].text_content()
    
    #ディレクトリを作成
    os.makedirs(csv_path, exist_ok=True)

    #csvファイル出力
    with open(csv_path + '/' + 'product_item.csv', 'a', encoding='utf8') as f:
        writer = csv.writer(
            f,
            delimiter=',',  # 区切り文字はカンマ
            quotechar='"',  # 囲い文字はダブルクォーテーション
            quoting=csv.QUOTE_NONNUMERIC    # 全ての非数値フィールドをクオート
        )

        writer.writerow([
          product_url,
          dirname,
          title,
          fixed_image_list[0],
          fixed_image_list[1],
          fixed_image_list[2],
          fixed_image_list[3],
          fixed_image_list[4],
          fixed_image_list[5],
          fixed_image_list[6],
          fixed_image_list[7],
          fixed_image_list[8],
          fixed_image_list[9],
          price,
          stock,
          explanation,
          translate(title),
          translate(explanation, 'ja', 'en', '。')
        ])


# In[10]:


#メルカリの商品ページをスクレイピングする
def scrape_mercari_item(product_url, csv_path, image_path, max_images, driver):    
    #print(datetime.datetime.now(), 'scrape_mercari_item')

    time.sleep(1)
    driver.get(product_url)

    #出品タイトル
    title = driver.find_element_by_xpath('//div[@id="item-info"]/section/div/mer-heading').get_attribute('title-label')

    #画像
    image_list = []
    for element in driver.find_elements_by_xpath('//div[@tabindex]/mer-item-thumbnail'):
        text = element.get_attribute('src')
        text = re.sub('\?.+', '', text)
        image_list.append(text)

    #ディレクトリを作成
    product_url_split_list = product_url.split("/")
    dirname = product_url_split_list[len(product_url_split_list)-1]
    os.makedirs(image_path + '/mercari/' + dirname, exist_ok=True)
    
    #画像を保存
    for index, image in enumerate(image_list):
      if index < max_images:
        image_split_list = image.split("/")
        filename = image_split_list[len(image_split_list)-1]
        r = requests.get(image).content
        with open(image_path + '/mercari/' + dirname + '/' + filename ,mode='wb') as f: # wb でバイト型を書き込める
          f.write(r)

    #画像のリストを固定長に変換
    fixed_image_list = [''] * 10
    for i in range(0, len(image_list)):
      fixed_image_list[i] = image_list[i]

    #価格
    price = driver.execute_script('return document.querySelector("#item-info > section:nth-child(1) > section:nth-child(2) > mer-text > mer-price").shadowRoot.querySelector("span.number")').get_attribute('textContent')
    
    #在庫の有無
    stock = 'out_of_stock'
    if len(driver.find_elements_by_xpath('//mer-button[@fluid and @intent="primary" and @data-testid and @mer-defined and @data-js-focus-visible and @type]')) > 0:
      stock = 'in_stock'
    
    #商品情報や説明文
    explanation = driver.execute_script('return document.querySelector("#item-info > section:nth-child(2) > mer-show-more > mer-text")').text

    #ディレクトリを作成
    os.makedirs(csv_path, exist_ok=True)

    #csvファイル出力
    with open(csv_path + '/' + 'product_item.csv', 'a', encoding='utf8') as f:
        writer = csv.writer(
            f,
            delimiter=',',  # 区切り文字はカンマ
            quotechar='"',  # 囲い文字はダブルクォーテーション
            quoting=csv.QUOTE_NONNUMERIC    # 全ての非数値フィールドをクオート
        )

        writer.writerow([
          product_url,
          dirname,
          title,
          fixed_image_list[0],
          fixed_image_list[1],
          fixed_image_list[2],
          fixed_image_list[3],
          fixed_image_list[4],
          fixed_image_list[5],
          fixed_image_list[6],
          fixed_image_list[7],
          fixed_image_list[8],
          fixed_image_list[9],
          price,
          stock,
          explanation,
          translate(title),
          translate(explanation)
        ])


# In[11]:


#ラクマの商品ページをスクレイピングする
def scrape_fril_item(product_url, csv_path, image_path, max_images, driver):    
    #print(datetime.datetime.now(), 'scrape_fril_item')

    time.sleep(1)
    driver.get(product_url)
    
    #出品タイトル
    title = driver.find_element_by_xpath('//h1[@class="item__name"]').get_attribute('textContent')

    #画像
    image_list = []
    for element in driver.find_elements_by_xpath('//img[@class="sp-image"]'):
        text = element.get_attribute('src')
        text = re.sub('\?.+', '', text)
        image_list.append(text)

    #ディレクトリを作成
    product_url_split_list = product_url.split("/")
    dirname = product_url_split_list[len(product_url_split_list)-1]
    os.makedirs(image_path + '/fril/' + dirname, exist_ok=True)
    
    #画像を保存
    for index, image in enumerate(image_list):
      if index < max_images:
        image_split_list = image.split("/")
        filename = image_split_list[len(image_split_list)-1]
        r = requests.get(image).content
        with open(image_path + '/fril/' + dirname + '/' + filename ,mode='wb') as f: # wb でバイト型を書き込める
          f.write(r)

    #画像のリストを固定長に変換
    fixed_image_list = [''] * 10
    for i in range(0, len(image_list)):
      fixed_image_list[i] = image_list[i]

    #価格
    text = driver.find_element_by_xpath('//span[@class="item__value"]').get_attribute('textContent')
    text = re.sub('\D', '', text)
    price = text
    
    #在庫の有無
    stock = 'in_stock'
    if len(driver.find_elements_by_xpath('//span[@id="btn_sold"]')) > 0:
      stock = 'out_of_stock'
    
    #商品情報や説明文
    explanation = driver.find_element_by_xpath('//div[@class="item__description"]').text

    #ディレクトリを作成
    os.makedirs(csv_path, exist_ok=True)

    #csvファイル出力
    with open(csv_path + '/' + 'product_item.csv', 'a', encoding='utf8') as f:
        writer = csv.writer(
            f,
            delimiter=',',  # 区切り文字はカンマ
            quotechar='"',  # 囲い文字はダブルクォーテーション
            quoting=csv.QUOTE_NONNUMERIC    # 全ての非数値フィールドをクオート
        )

        writer.writerow([
          product_url,
          dirname,
          title,
          fixed_image_list[0],
          fixed_image_list[1],
          fixed_image_list[2],
          fixed_image_list[3],
          fixed_image_list[4],
          fixed_image_list[5],
          fixed_image_list[6],
          fixed_image_list[7],
          fixed_image_list[8],
          fixed_image_list[9],
          price,
          stock,
          explanation,
          translate(title),
          translate(explanation)
        ])


# In[12]:


#翻訳
#文字数の制約ありのため500文字ずつ翻訳する
def translate(text, source='ja', target='en', delimiter='\n'):
    global script_url_list_index
    
    #print(datetime.datetime.now(), 'translate')

    #改行コードで分割
    text_list = text.split(delimiter)

    target_text = ''

    target_text_list = []

    for t in text_list:
      target_text = target_text + t + delimiter

      #500文字を超えたら分割
      if len(target_text) > 500:
        target_text_list.append(target_text)
        target_text = ''

    #分割なしまたは分割ありの最後の文字列を追加
    if len(target_text) != 0:
      target_text_list.append(target_text)
      target_text = ''

    #最後の改行コードを削除
    target_text_list[len(target_text_list) - 1] = re.sub(delimiter + '$', '', target_text_list[len(target_text_list) - 1])

    translate_target_text = ''

    for tt in target_text_list:
      script_url = script_url_list[script_url_list_index]
      
      time.sleep(1)
      r = requests.get(script_url + '?text=' + urllib.parse.quote(tt) + '&source=' + source + '&target=' + target)

      translate_target_text = translate_target_text + r.text

      #翻訳用URLのindexをラウンドロビン
      script_url_list_index += 1

      if script_url_list_index > (len(script_url_list)) - 1:
        script_url_list_index = 0

    return translate_target_text


# In[22]:


#python -m scrape_7846329.py url csv_path image_path max_images max_items

#・ヤフオク
#　カテゴリのURL：https://auctions.yahoo.co.jp/category/list/2084261693/?p=%E3%83%8B%E3%82%B3%E3%83%B3&auccat=2084261693&fixed=1&exflg=1&b=1&n=100&s1=featured&mode=2
#
#　検索のURL：https://auctions.yahoo.co.jp/search/search?p=Nikon+MF%E3%83%AC%E3%83%B3%E3%82%BA&va=Nikon+MF%E3%83%AC%E3%83%B3%E3%82%BA&fixed=1&exflg=1&b=1&n=100&mode=2
#
#・メルカリ
#　カテゴリのURL：https://jp.mercari.com/search?brand_id=2905&page=1&t3_category_id=414&t2_category_id=39&t1_category_id=2&category_id=414
#
#　検索のURL：https://jp.mercari.com/search?keyword=g-shock&page=1
#
#・ラクマ
#　カテゴリのURL：https://fril.jp/s?query=%E3%83%95%E3%82%A1%E3%83%9F%E3%82%B3%E3%83%B3&category_id=788&transaction=selling
#
#　検索のURL：https://fril.jp/s?query=%E3%83%95%E3%82%A1%E3%83%9F%E3%82%B3%E3%83%B3%E3%82%BD%E3%83%95%E3%83%88&transaction=selling

if __name__ == '__main__':
    #すべての警告を表示させない
    warnings.simplefilter('ignore')

    print(datetime.datetime.now(), '処理を開始します')

    for index, argv in enumerate(sys.argv):
      print(datetime.datetime.now(), 'argv[' + str(index) + ']', argv)
    
    #本番用
    url = sys.argv[1]
    csv_path = sys.argv[2]
    image_path = sys.argv[3]
    max_images = int(sys.argv[4])
    max_items = int(sys.argv[5])

    #テスト用
    #ヤフオク検索
    #url = 'https://auctions.yahoo.co.jp/search/search?auccat=2084005573&tab_ex=commerce&ei=utf-8&aq=1&oq=python&exflg=1&p=python&x=0&y=0&sc_i=auc_sug_cat'
    #ヤフオクカテゴリ
    #url = 'https://auctions.yahoo.co.jp/category/list/2084006413/?p=%E3%83%A2%E3%83%87%E3%83%AB%E3%82%AC%E3%83%B3&auccat=2084006413&exflg=1&b=1&n=50&s1=featured&brand_id=104070'
    #ヤフオク商品
    #url = 'https://page.auctions.yahoo.co.jp/jp/auction/u1011344897'
    #メルカリ検索
    #url = 'https://jp.mercari.com/search?keyword=python%20ai%20%E5%85%A5%E9%96%80&page=1'
    #メルカリ商品
    #url = 'https://jp.mercari.com/item/m44254990996'
    #ラクマ検索
    #url = 'https://fril.jp/s?query=python+ai'
    #ラクマ商品
    #url = 'https://item.fril.jp/5a8182901190807409a619e8eb465ebc'   

    #url = 'https://auctions.yahoo.co.jp/category/list/2084261693/?p=%E3%83%8B%E3%82%B3%E3%83%B3&auccat=2084261693&fixed=1&exflg=1&b=1&n=100&s1=featured&mode=2'
    #url = 'https://auctions.yahoo.co.jp/search/search?p=Nikon+MF%E3%83%AC%E3%83%B3%E3%82%BA&va=Nikon+MF%E3%83%AC%E3%83%B3%E3%82%BA&fixed=1&exflg=1&b=1&n=100&mode=2'
    #url = 'https://jp.mercari.com/search?brand_id=2905&page=1&t3_category_id=414&t2_category_id=39&t1_category_id=2&category_id=414'
    #url = 'https://jp.mercari.com/search?keyword=g-shock&page=1'
    #url = 'https://fril.jp/s?query=%E3%83%95%E3%82%A1%E3%83%9F%E3%82%B3%E3%83%B3&category_id=788&transaction=selling'
    #url = 'https://fril.jp/s?query=%E3%83%95%E3%82%A1%E3%83%9F%E3%82%B3%E3%83%B3%E3%82%BD%E3%83%95%E3%83%88&transaction=selling'

    #csv_path = 'csv'
    #image_path = 'image'
    #max_images = int(1)
    #max_items = int('10')
    
    #chromeを開く
    driver = start_chrome()
    #driver = start_chrome_colab() #google colaboratory用
    
    product_url_list = []
    
    print(datetime.datetime.now(), '商品URLを取得します', url)

    #検索ページから商品URLを取得する
    if 'auctions.yahoo.co.jp/search' in url or 'auctions.yahoo.co.jp/category' in url:
      while True:
        try:
          time.sleep(1)
          driver.get(url)

          #for element in driver.find_elements_by_xpath('//li[@class="Product"]/div/a'):
          for element in driver.find_elements_by_xpath('//li[contains(@class, "Product")]/div/a'): #表示形式mode=4の対応
            product_url_list.append(element.get_attribute('href'))
            #最大件数を超えたらやめる
            if len(product_url_list) >= max_items:
              break
          
          #最大件数を超えたらやめる
          if len(product_url_list) >= max_items:
            break
          
          #ページング処理
          if len(driver.find_elements_by_xpath('//li[@class="Pager__list Pager__list--next"]/a')) == 0:
            break
        except: 
          import traceback
          traceback.print_exc()
        
        url = driver.find_element_by_xpath('//li[@class="Pager__list Pager__list--next"]/a').get_attribute('href')
    elif 'jp.mercari.com/search' in url:
      time.sleep(1)
      driver.get(url)
      while True:
        try:
          for element in driver.find_elements_by_xpath('//li[@data-testid="item-cell"]/a'):
            product_url_list.append(element.get_attribute('href'))
            #最大件数を超えたらやめる
            if len(product_url_list) >= max_items:
              break

          #最大件数を超えたらやめる
          if len(product_url_list) >= max_items:
            break

          if len(driver.find_elements_by_xpath('//mer-button[@data-testid="pagination-next-button"]')) == 0:
            break

          #ポップアップが開いていれば閉じる
          try:
            driver.execute_script('document.querySelector("body > mer-information-popup").shadowRoot.querySelector("#modal > mer-icon-button").shadowRoot.querySelector("div").click()')
          except:
            pass
          #次へボタンまでスクロール
          driver.execute_script('arguments[0].scrollIntoView(true);', driver.find_element_by_xpath('//mer-button[@data-testid="pagination-next-button"]'))
          
          #ページング処理
          driver.find_element_by_xpath('//mer-button[@data-testid="pagination-next-button"]').click()
          time.sleep(1)
        except: 
          import traceback
          traceback.print_exc()        
    elif 'fril.jp/s?' in url:
      for i in range(1, 101, 1):
        try:
          time.sleep(1)
          driver.get(url + '&page=' + str(i))

          for element in driver.find_elements_by_xpath('//div[@class="item"]/div/div/a'):
            product_url_list.append(element.get_attribute('href'))
            #最大件数を超えたらやめる
            if len(product_url_list) >= max_items:
              break
          
          #最大件数を超えたらやめる
          if len(product_url_list) >= max_items:
            break

          #ページング処理
          if len(driver.find_elements_by_xpath('//div[@class="item"]/div/div/a')) == 0:
            break
        except: 
          import traceback
          traceback.print_exc() 
    else:
      product_url_list.append(url)
    
    print(datetime.datetime.now(), '商品情報を取得します')
        
    #商品URLのリストから商品情報を取得する
    for index, product_url in enumerate(product_url_list):
      print(datetime.datetime.now(), str(index + 1) + '/' + str(len(product_url_list)) + 'を処理しています', product_url)
      if 'page.auctions.yahoo.co.jp' in product_url:
          scrape_yahoo_item(product_url, csv_path, image_path, max_images, driver)  
          #scrape_yahoo_item_requests(product_url, csv_path, image_path, max_images)  
      elif 'jp.mercari.com/item' in product_url:
          scrape_mercari_item(product_url, csv_path, image_path, max_images, driver)  
      elif 'item.fril.jp' in product_url:
          scrape_fril_item(product_url, csv_path, image_path, max_images, driver)
        
    #chromeを閉じる
    end_chrome(driver)
    
    print(datetime.datetime.now(), '処理を終了します')

    sys.exit(0)


# In[1]:


#pyファイルへ変換する
get_ipython().system('jupyter nbconvert --to python scrape_7846329_colab_pc.ipynb')


# In[15]:


#exeファイルを作成する
get_ipython().system('pyinstaller scrape_7846329.py --noconfirm')


# In[ ]:




