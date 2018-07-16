import urllib.request
from lxml import etree
import traceback
import sqlite3
import time
import ssl
from urllib import request
import re
from bs4 import BeautifulSoup
url="https://qc.sentinel1.eo.esa.int/aux_poeorb/"
header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'qc.sentinel1.eo.esa.int',
        'Referer': url,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }



req = urllib.request.Request(url,headers=header)
response = urllib.request.urlopen(req)
html=response.read()
page = etree.HTML(html)
for link in page.xpath('//@href'):
    print(link)

bsObj = BeautifulSoup(html, 'html.parser')
t1 = bsObj.find_all('a')
for t2 in t1:
    t3 = t2.get('href')
    print(t3)

print('done')