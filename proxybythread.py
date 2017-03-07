#!/usr/bin/env python
# coding=utf-8

import MySQLdb as mdb
import requests
from threading import Thread

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '910830gz',
    'db': 'proxies',
    'charset': 'utf8'
}
url = "http://www.meituan.com"
head = {
    'Host': "www.meituan.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}


def checkproxy(ip, port, flag):
    s = "http://" + str(ip) + ":" + str(port)
    proxy = {"http": s}
    try:
        req = requests.get(url, head, proxies=proxy, timeout=30)
        if req.status_code == 200 and flag == 0:
            cour.execute('update proxyspool SET flag = %s WHERE ip = "%s"' % (1, ip))
            conn.commit()
    except requests.exceptions.RequestException as e:
        if flag == 1:
            cour.execute('update proxyspool SET flag = %s WHERE ip = "%s"' % (0, ip))
            conn.commit()
    except mdb.Error as e:
        print e


if __name__ == '__main__':
    conn = mdb.connect(**config)
    cour = conn.cursor()
    n = cour.execute("select * from proxyspool")
    threads = []
    for row in cour.fetchall():
        ip1 = row[1]
        port1 = row[2]
        flag1 = row[3]
        threads.append(Thread(target=checkproxy, args=(ip1, port1, flag1)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    cour.close()
    conn.close()
