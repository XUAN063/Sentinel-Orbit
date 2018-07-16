import time
import datetime
import sqlite3
import os
import shutil
import orbit
from urllib.request import urlretrieve

def Establish_Database(Database_name):
    '''建立轨道数据的数据库
        args:
            Database_name:数据库名
        数据库字段:
            ID:轨道参数的ID号,为系统自动生成
            Platform:卫星的平台属性,S1A和S1B
            FileNmae:轨道文件的文件名
            Date1_UTC:轨道起始时间的UTC秒
            Date2_UTC:轨道数据结束时刻的UTC秒
            DownLoad_url:轨道数据的下载链接
    '''
    conn = sqlite3.connect(Database_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE EOF
        (ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        Platform        TEXT     NOT NULL,
        FileName        TEXT        NOT NULL,
        Date1_UTC       REAL        NOT NULL,
        Date2_UTC       REAL        NOT NULL,
        DownLoad_url    TEXT        NOT NULL);''')
    conn.commit()
    print("Table created successfully")
    conn.close()
    return True


def Fill_Data(href_list, dbname):
    '''向数据中的EOF表中填充轨道参数数据
        Args:
            href_list:所有轨道参数下载链接文件
            dbname:数据库名称
    '''

    # 链接数据库
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    idx = 1
    for tmp in href_list:
        tmp = tmp.replace("\n", "")

        # 从下载链接中提取文件名,平台,起始时间等
        FileName = (tmp.split('/'))[-1]
        PlatForm = str(FileName[0:3])
        date1 = str(time.mktime(time.strptime(tmp[92:100], '%Y%m%d')))
        date2 = str(time.mktime(time.strptime(tmp[108:116], '%Y%m%d')))

        value = "VALUES (" + "'" + PlatForm + "'" + ',' + "'" + FileName + \
            "'" + ',' + date1 + "," + date2 + "," + "'" + tmp + "'" + ")"

        sql = "INSERT INTO EOF (Platform,FileName,Date1_UTC,Date2_UTC,DownLoad_url)" + value
        c.execute(sql)

        print(idx)
        idx = idx+1

    conn.commit()
    conn.close()


def Select_Eof(Name_list_file, idf):
    '''根据输入的文件名文件选择出相应的轨道数据
        Args:
            Name_list_file:下载数据的文件名列表
            idf:确定获取的为哪个字段
        Return:
            返回选择出的轨道数据下载连接
    '''

    # 输出结果列表
    Eof_list = []

    # 链接数据库并获取游标
    conn = sqlite3.connect('eof.db')
    c = conn.cursor()

    # 读取所有的文件名存放在Name_list中
    name_list = []
    with open(Name_list_file) as fid:
        name_list = fid.readlines()

    # 遍历文件名列表进行提取
    for tmp_name in name_list:
        # 获取卫星的平台和影像获取日期(UTC秒)
        platform = tmp_name[0:3]
        date_utc = time.mktime(time.strptime(tmp_name[17:25], '%Y%m%d'))

        # 从数据库中选出符合条件的下载链接
        sql = "SELECT * FROM EOF WHERE" + " Platform == " + "'" + platform + "'" + \
            " AND " + "Date1_UTC < " + \
            str(date_utc) + " AND Date2_UTC > " + str(date_utc)

        res = c.execute(sql).fetchall()

        if len(res) != 0:
            if idf == 'name':
                Eof_list.append(res[0][2])
            else:
                Eof_list.append[res[0][5]]

        else:
            Eof_list.append('NULL')
            print('未查询到此文件对应的轨道数据:  ' + tmp_name)
    conn.close()
    return Eof_list


def pick_file(Eof_name_list, out_dir):
    '''根据输入的轨道参数列表和输出路径提取轨道数据到指定目录
        Args:
            Eof_name_list:需要提取的轨道文件的文件名
            out_dir:轨道文件的输出目录
    '''
    res_idf = False

    # 获取当前目录
    Data_Dir = os.getcwd()+"\\DataSet\\"

    if not os.path.exists(out_dir):
        print("当前目录不存在")
        return res_idf

    idx = 1
    for tmp_name in Eof_name_list:
        abs_Path = Data_Dir+tmp_name

        if os.path.exists(abs_Path):
            shutil.copy(abs_Path, out_dir)
        else:
            print('此文件不存在:  ' + tmp_name)

        print('正在复制第----  '+str(idx)+' --文件')
        idx = idx+1

    return True


def init_database(dbname):
    ''' Function:初始化数据(新建数据库,数据表,字段)
        Args:
            dbname:数据库的名称
    '''
    if Establish_Database(dbname):
        print('数据库已建立')
        f = open('href_all.txt')
        href_all = f.readlines()
        href_all.reverse()
        Fill_Data(href_all, dbname)
        print('数据初始化成功')


def cbk(a, b, c):
    '''回调函数,下载文件的进度条
    @a:已经下载的数据块
    @b:数据块的大小
    @c:远程文件的大小
    '''
    per = 100.0*a*b/c
    if per > 100:
        per = 100
    print('%.1f%%' % per)


def Eof_Update(dbname):
    '''数据库的更新程序,获取网站上当前最新数据进行更新'''
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    sql = "SELECT MAX(Date1_UTC) FROM EOF"
    max_id = c.execute(sql).fetchall()[0][0]

    sql = "SELECT * FROM EOF WHERE Date1_UTC == "+str(max_id)
    recent_url = c.execute(sql).fetchall()[0][5]
    conn.close()

    update_href = orbit.Orbit_Update(recent_url)
    Fill_Data(update_href, dbname)

    idx = 1
    for cur_url in update_href:
        print('正在下载第-----  '+str(idx)+' -----文件')
        file_name = os.getcwd()+"\\DataSet\\" + (cur_url.split('/'))[-1]
        urlretrieve(cur_url, file_name, cbk)
    print('数据库更新完成')

def orbit_select(list_file, out_dir):
    '''根据输入的下载列表文件和输出路径提取相应的轨道数据
        args:
            list_file:存储下载影像文件名的文件
            out_dir:轨道数据的输出目录
    '''
    Eof_Update('eof.db')
    name_list = Select_Eof(list_file, 'name')
    pick_file(name_list, out_dir)
