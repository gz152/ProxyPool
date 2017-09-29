#!/usr/bin/python
# coding=utf-8

import Queue
import pymysql as mdb
import requests
from threading import Thread
import time

queueproxy = Queue.Queue(24)
goodproxyip = []
badproxyip = []
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '910830gz',
    'db': 'proxies',
    'charset': 'utf8'
}


class GetProxyinDB(Thread):

    """docstring for GetProxyinDB"""

    def __init__(self, cur):
        super(GetProxyinDB, self).__init__()
        self.cur = cur

    def run(self):
        global queueproxy
        while 1:
            row = self.cur.fetchone()
            if row is None:
                queueproxy.put(None)
                break
            queueproxy.put(row)
            time.sleep(1)


class CheckProxy(Thread):

    """docstring for CheckProxy"""

    def __init__(self, url, head):
        super(CheckProxy, self).__init__()
        self.url = url
        self.head = head

    def run(self):
        global queueproxy
        global goodproxyip
        global badproxyip
        while 1:
            res = queueproxy.get()
            if res is None:
                break
            protoc, ip, port, flag = res
            s = ''.join((str(protoc), "://", str(ip), ":", str(port)))
            proxy = {protoc: s}

            try:
                req = requests.get(
                    self.url, self.head, proxies=proxy, timeout=3)
                if req.status_code != 200 and flag == 1:
                    badproxyip.append(ip)
                elif req.status_code == 200 and flag == 0:
                    goodproxyip.append(ip)
            except requests.exceptions.RequestException:
                if flag == 1:
                    badproxyip.append(ip)

if __name__ == '__main__':
    conn = mdb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("select * from proxyspool")

    url = "http://www.meituan.com"
    head = {
        'Host': "www.meituan.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/56.0.2924.87 Safari/537.36"
    }

    getList = []
    checkList = []

    for i in xrange(12):
        get = GetProxyinDB(cursor)
        getList.append(get)
        check = CheckProxy(url, head)
        checkList.append(check)

    for i, j in zip(getList, checkList):
        i.start()
        j.start()
    for i, j in zip(getList, checkList):
        i.join()
        j.join()
    
    for ip in goodproxyip:
        cursor.execute('update proxyspool SET flag = %s WHERE ip = "%s"' % (1, ip))
    for ip in badproxyip:
        cursor.execute('update proxyspool SET flag = %s WHERE ip = "%s"' % (0, ip))
    conn.commit()
    cursor.close()
    conn.close ()
