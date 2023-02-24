#%%
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import multiprocessing as mp
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import re
import chromedriver_autoinstaller
path = chromedriver_autoinstaller.install(".")
from random import randint
#%%
def getInfo(info_list):
    pattern = r'"(.*)" '
    item_search = re.search(pattern, info_list[0]).group(1)
    pattern = r"\>(.*)\<"
    bigger = re.search(pattern, info_list[2]).group(1)
    smaller = re.search(pattern, info_list[3]).group(1)
    return [item_search, bigger, smaller]

def checkValid(s, p):
    str_ok = False
    q = 0
    if len(p) > 1:
        for i in range(len(p) - 1):
            if s.count(p[i:i+2]) > q:
                print("common string is ", p[i:i+2])
                q = s.count(p[i:i+1])
    if q >= 1 or len(p) == 1:
        str_ok = True
    return str_ok

#%%
def updateUniItem(item):
    item = str(item)
    search_item = re.sub('[0-9a-zA-Z]+', '', item)
    search_item = search_item.replace("型號", "")
    options = Options()
     # docker原本的分享記憶體在 /dev/shm 是 64MB，會造成chorme crash，所以要改成寫入到 /tmp
    options.add_argument('--disable-dev-shm-usage')
    # 以最高權限運行
    options.add_argument('--no-sandbox')
    # google document 提到需要加上這個屬性來規避 bug
    options.add_argument('--disable-gpu')
    # 做完事就停擺
    # options.add_experimental_option("detach", True)
    if search_item[-6:] == "":
        new = pd.DataFrame(np.array([item, '', '', ''])).T
        new.columns = ["pre_compress", "item_search", "bigger", "smaller"]
        return new
    try:
        time.sleep(randint(1,3))
        chrome = webdriver.Chrome(options=options, executable_path=path)
        chrome.maximize_window()
        chrome.get("https://shop.pxmart.com.tw/v2/official/SalePageCategory/250?sortMode=Sales")
        time.sleep(1)
        try:
            search_edit = chrome.find_elements(By.XPATH, '//*[@id="ns-search-input"]')[0]
            search_edit.send_keys(search_item[-6:])
            search_but = chrome.find_elements(By.XPATH, '//*[@id="root"]/div/div[1]/section/header/section/section/nav/div/span/form/div/a')[0]
            search_but.click()
        except:
            print(f"Item：{search_item} forbibben happens... Go to Sleep")
            chrome.close()
            time.sleep(70)
            print(f"Item：{search_item} Wake up and keep going on")
            chrome = webdriver.Chrome(options=options)
            chrome.maximize_window()
            chrome.get("https://shop.pxmart.com.tw/v2/official/SalePageCategory/250?sortMode=Sales")
            time.sleep(1)
            search_edit = chrome.find_elements(By.XPATH, '//*[@id="ns-search-input"]')[0]
            search_edit.send_keys(search_item[-6:])
            search_but = chrome.find_elements(By.XPATH, '//*[@id="root"]/div/div[1]/section/header/section/section/nav/div/span/form/div/a')[0]
            search_but.click()
            time.sleep(0.5)
        
        img_but = chrome.find_elements(By.XPATH, ' //*[@id="root"]/div/div[2]/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/div/div/ul/li[1]/div/div/a/div/div[1]/figure/img')[0]
        img_but.click()
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        soup.prettify()
        info_list = [str(x) for x in soup.find_all(itemprop = "name")]
        item_search, bigger, smaller = getInfo(info_list)
        print(search_item, item_search)
        if checkValid(search_item, item_search):
            new = pd.DataFrame(np.array([item, item_search, bigger, smaller])).T
        else:
            new = pd.DataFrame(np.array([item, '', '', ''])).T
        new.columns = ["pre_compress", "item_search", "bigger", "smaller"]
        time.sleep(randint(1,3))
    except:
        new = pd.DataFrame(np.array([item, '', '', ''])).T
        new.columns = ["pre_compress", "item_search", "bigger", "smaller"]
    try:
        chrome.close()
    except: pass
    return new
#%%
c = 0
updateNum = 20
limit = 20
ChromeDriverManager().install()
data = pd.read_excel(f"D:\Dropbox\Andy\invoice\\display20\\display20.xlsx")
noImpChar = [" ", "1", "2", "3", "4", "(", ")", "5", "-", "6", "7", "8", "9", "0", "/", "[", "]", ".", "o", r"*", "+", "$", "%", "@", "#", "（", "）", ":", "【", "】", "－", "=", ",", "\u3000", "_", "~", "?"]
data["pre_compress"] = data["items"]
for i in noImpChar:
    data["pre_compress"] = data["pre_compress"].str.replace(i, "")
classWords = data.pre_compress.unique()

# uni_items_df = pd.DataFrame(columns = ["pre_clsfy", "item_search", "bigger", "smaller"])
uni_items_df = pd.read_excel(f"D:\Dropbox\Andy\invoice\\display20\\search.xlsx")
if __name__ == '__main__':
    pool = mp.Pool(processes=8)
   
    intercept = uni_items_df.shape[0] + c
    
    for j in range(1000):
        if j *  updateNum + intercept > limit:
            break
        print(j *  updateNum + intercept, "~", (j + 1) * updateNum + intercept)
        news = pool.map(updateUniItem, classWords[j *  updateNum + intercept: (j + 1) * updateNum + intercept])
        for new in news:
            uni_items_df = pd.concat([uni_items_df, new])
        print("----------------- \nprepare update \n----------------------")
        uni_items_df.to_excel(f"D:\Dropbox\Andy\invoice\\display20\\search.xlsx", index = False)
#%%
# uni_items_df
# # %%
# soup.prettify()
# info_list = [str(x) for x in soup.find_all(itemprop = "name")]
# # %%

# pattern = r'"(.*)" '
# item_search = re.search(pattern, info_list[0]).group(1)
# pattern = r"\>(.*)\<"
# bigger = re.search(pattern, info_list[2]).group(1)
# smaller = re.search(pattern, info_list[3]).group(1)

# %%
