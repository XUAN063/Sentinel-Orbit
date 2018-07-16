from urllib import request
from lxml import etree
import traceback
import sqlite3
import time
import ssl
import datetime

# 创建https的加密证书
ssl._create_default_https_context = ssl._create_unverified_context


def hrefFromPage(url):
    '''获取当前网页中所有的下载连接
        Args:
            url:当前网页的地址
        return:返回网页上下载连接的list
    '''

    # 构造请求头
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

    hrefList = []
    req = request.Request(url, headers=header)
    global response
    try:
        response = request.urlopen(req, timeout=60)
    except:
        traceback.print_exc()

    global page
    try:
        page = etree.HTML(response.read())
    except:
        print('done')
    for link in page.xpath('//@href'):
        if(link[0:4] == "http"):
            hrefList.append(link)
    return hrefList


def getDateList(filePath):
    '''根据文件名的文本文件获取成像日期列表
        Args:
            filePath:存储文件名的文本文件
        return:
            返回成像的日期列表
    '''
    dateList = []
    fid = open(filePath, 'r')
    nameList = fid.readlines()
    fid.close()

    for line in nameList:
        dateList.append([line[17:25]])
    dateList.sort()
    return dateList


def getAllHref():
    '''所有的下载链接
        Args:
            earliestDate:影像最早成像日期
        return:
            返回覆盖影像成像日期内的所有轨道数据
    '''
    allHrefList = []

    cur_hrefList = hrefFromPage('https://qc.sentinel1.eo.esa.int/aux_poeorb/')
    print('正在读取----', 1, '-----页')

    allHrefList = allHrefList+cur_hrefList
    page_num = 2
    while True:
        cur_hrefList = hrefFromPage(
            'https://qc.sentinel1.eo.esa.int/aux_poeorb/?page='+str(page_num))

        allHrefList = allHrefList+cur_hrefList
        time.sleep(0.5)

        if len(cur_hrefList) < 20:
            break

        print('正在读取----', page_num, '-----页')
        page_num += 1

    return allHrefList


def select_eof(eof_file, download_file):
    ''' 从
    '''
    fid = open(eof_file)
    eof_list = fid.readlines()
    fid.close()

    fid = open(download_file)
    url_list = fid.readlines()
    fid.close()

    res = []

    setp = 1
    for tmp_url in url_list:

        url_date = datetime.datetime.strptime(tmp_url[17:25], '%Y%m%d')
        print(setp)
        setp = setp+1
        for tmp_eof in eof_list:

            eof_date1 = datetime.datetime.strptime(tmp_eof[92:100], '%Y%m%d')
            eof_date2 = datetime.datetime.strptime(tmp_eof[108:116], '%Y%m%d')

            dif1 = (url_date-eof_date1).days
            dif2 = (url_date-eof_date2).days
            if dif1 > 0 and dif2 < 0:
                res.append(tmp_eof)
                break

    return res


def Orbit_Update(url):
    '''Function:根据输入的下载链接获取网页上新增链接
        Args:
            url:数据库中时间最新的轨道数据下载链接
    '''
    hreflist = []
    idx = 1

    while True:
        cur_page_list = hrefFromPage(
            'https://qc.sentinel1.eo.esa.int/aux_poeorb/?page='+str(idx))

        hreflist = hreflist+cur_page_list

        date1 = time.mktime(time.strptime(url[92:100], '%Y%m%d'))
        page_last_date1 = time.mktime(
            time.strptime(cur_page_list[-1][92:100], '%Y%m%d'))

        idx = idx+1
        if page_last_date1 < date1:
            break

    add_list = []
    for tmp in hreflist:
        if tmp == url:
            break
        add_list.append(tmp)
    return add_list
