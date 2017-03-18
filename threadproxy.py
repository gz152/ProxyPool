#!/usr/bin/env python
# coding=utf-8

import Queue
import MySQLdb as mdb
import requests
from threading import Thread
import time

queueproxy = Queue.Queue(20)
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
                print 'come to the end'
                break
            print row
            queueproxy.put(row)
            time.sleep(1)


class CheckProxy(Thread):

    """docstring for CheckProxy"""

    def __init__(self, cur, conn, url, head):
        super(CheckProxy, self).__init__()
        self.cur = cur
        self.conn = conn
        self.url = url
        self.head = head

    def run(self):
        global queueproxy
        while 1:
            res = queueproxy.get()
            if res is None:
                print "get a None"
                break
            _, ip, port, flag = res
            print queueproxy.qsize()
            s = ''.join(("http://", str(ip), ":", str(port)))
            proxy = {"http": s}

            try:
                req = requests.get(
                    self.url, self.head, proxies=proxy, timeout=5)
                if req.status_code == 200 and flag == 0:
                    self.cur.execute(
                        'update proxyspool SET flag = %s WHERE ip = "%s"' % (1, ip))
                   # self.conn.commit()
            except requests.exceptions.RequestException:
                if flag == 1:
                    self.cur.execute(
                        'update proxyspool SET flag = %s WHERE ip = "%s"' % (0, ip))
                   # self.conn.commit()

if __name__ == '__main__':
    conn = mdb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("select * from proxyspool")

    url = "http://www.xicidaili.com"
    head = {
        'Host': "www.xicidaili.com",
        'Referer': "http://www.xicidaili.com/nn/",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
         Chrome/56.0.2924.87 Safari/537.36",
        'Connection': 'keep-alive'
    }

    getList = []
    checkList = []

    for i in xrange(10):
        get = GetProxyinDB(cursor)
        getList.append(get)
        check = CheckProxy(cursor, conn, url, head)
        checkList.append(check)

    for i, j in zip(getList, checkList):
        i.start()
        j.start()
    for i, j in zip(getList, checkList):
        i.join()
        j.join()
        
    conn.commit()
    print "will close dbconnection!"
    cursor.close()
    conn.close()
