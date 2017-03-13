#!/usr/bin/env python
# coding=utf-8

# Author: GuoZheng
# Mail: gzcug2010@gmail.com
# Created Time: Mon 27 Feb 2017 04:54:15 PM CST

import MySQLdb as mdb
import requests

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '910830gz',
    'db': 'proxies',
    'charset': 'utf8'
}

def check_proxy(url, head, con, cour):
    
    n = cour.execute("select * from proxyspool")
    for row in cour.fetchall():
        ip = row[1]
        port = row[2]
        fg = row[3]
        s = "http://" + str(ip) + ":" + str(port)
        proxy = {"http": s}
        try:
            req = requests.get(url=url, headers=head, proxies=proxy,timeout=5)
            if req.status_code == 200 and fg == 0:
                cour.execute('update proxyspool SET flag = %s WHERE ip = "%s"' %(1,ip))
                con.commit()
        except requests.exceptions.RequestException:
            if fg == 1:
                cour.execute('update proxyspool SET flag = %s WHERE ip = "%s"' %(0,ip))
                con.commit()
        except mdb.Error as e:
            print e

url = "http://www.meituan.com"
head = {
    'Host': "www.meituan.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}

if __name__ == '__main__':
    conn = mdb.connect(**config)
    coursor = conn.cursor()
    check_proxy(url, head, conn, coursor)
    coursor.close()
    conn.close()

