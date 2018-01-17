#!/usr/bin/env python
# coding=utf-8

import queue
import pymysql as mdb
from threading import Thread
import time
import checkProxyof

queueproxy = queue.Queue(24)
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

    def __init__(self):
        super(CheckProxy, self).__init__()

    def run(self):
        global queueproxy
        global goodproxyip
        global badproxyip
        while 1:
            res = queueproxy.get()
            if res is None:
                break
            protoc, ip, port, flag = res

            statuscode = checkProxyof.checkproxy(protoc, ip, port)
            if statuscode != 200 and flag == 1:
                badproxyip.append(ip)
            elif statuscode == 200 and flag == 0:
                goodproxyip.append(ip)

if __name__ == '__main__':
    conn = mdb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("select * from proxyspool")

    getList = []
    checkList = []

    for i in range(12):
        get = GetProxyinDB(cursor)
        getList.append(get)
        check = CheckProxy()
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
