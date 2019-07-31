#!/usr/bin/env python
# coding: utf-8

# * download(method, url, param=None, data=None, timeout=1, maxretries=3)
# * parseURL(seed)
# 

# import os, sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# import crawling

# In[1]:


import requests
import time
from bs4 import BeautifulSoup

headers = {"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}

def download(method, url, param=None, data=None, timeout=1, maxretries=3):
    try:
        resp = requests.request(method, url, params=param, data=data, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if 500 <= e.response.status_code < 600         and maxretries > 0:
            print(maxretries)
            time.sleep(timeout)
            resp = download(method, url, param, data, timeout, maxretries-1)
            #print("재시도")
        else:
            print(e.response.status_code)
            print(e.response.reason)
    return resp


# In[2]:


def parseURL(seed):
    urlList = list()
    
    html = download("get", seed)
    dom = BeautifulSoup(html.text, "lxml")
    
    return [requests.compat.urljoin(url, _["href"]) for _ in dom.find_all("a") if _.has_attr("href") and len(_["href"]) > 3]


# In[ ]:




