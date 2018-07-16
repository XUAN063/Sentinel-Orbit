import sqlite3
import datetime
import time

global href
with open('href_all.txt') as fid:
    href = fid.readlines()

href.reverse()

conn = sqlite3.connect('test.db')
c = conn.cursor()

idx = 1

for tmp in href:
    tmp = tmp.replace("\n", "")

    FileName = (tmp.split('/'))[-1]
    PlatForm = str(FileName[0:3])
    date1 = str(time.mktime(time.strptime(tmp[92:100], '%Y%m%d')))
    date2 = str(time.mktime(time.strptime(tmp[108:116], '%Y%m%d')))

    value = "VALUES (" + "'" + PlatForm + "'" + ',' + "'" + FileName + "'" + ',' + date1 + \
        "," + date2 + "," + "'" + tmp + "'" + ")"

    sql = "INSERT INTO EOF (Platform,FileName,Date1_UTC,Date2_UTC,DownLoad_url)" + value

    c.execute(sql)
    print(idx)
    idx = idx+1

conn.commit()

res = c.execute('''select * from EOF''')
all_res = res.fetchall()

idx = 1
for tt in all_res:

    if idx >= 10:
        break
    idx = idx+1
    print(tt)
    print('\n')
conn.close()
