#!/usr/bin/env python
# coding=utf-8

# Author: GuoZheng
# Mail: gzcug2010@gmail.com
# Created Time: Thu 23 Feb 2017 02:23:09 PM CST

from bs4 import BeautifulSoup
import requests
import re
import MySQLdb as mdb

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '910830gz',
    'db': 'proxies',
    'charset': 'utf8'
}


def get_proxy(url, head):
    page = requests.get(url=url, headers=head)
    print page.status_code

    soup = BeautifulSoup(page.text, 'lxml')
    res_ip = soup.find_all(text=re.compile("^\d+\.\d+\.\d+\.\d+$"))
    res_port = soup.find_all('td', text=re.compile("^\d+$"))

    for ip, port in zip(res_ip, res_port):
        yield (ip.string, port.string)


def check_proxy(url, head, con, cour):
    for ip,port in get_proxy(url, head):
        s = "http://" + str(ip) + ":" + str(port)
        proxy = {"http": s}
        try:
            req = requests.get(url=url, headers=head, proxies=proxy,timeout=3)
        except requests.exceptions.RequestException:
            continue
        if req.status_code == 200:
            value = ("http", str(ip), int(port),1)
            cour.execute('INSERT into proxyspool values(%s,%s,%s,%s)',value)
            con.commit()

url = "http://www.xicidaili.com/nn/"
head = { 
    'Host': "www.xicidaili.com",
    'Referer': "http://www.xicidaili.com/nn/",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'Connection': 'keep-alive'
}

if __name__ == '__main__':
    conn = mdb.connect(**config)
    coursor = conn.cursor()
    check_proxy(url, head, conn, coursor)
    coursor.close()
    conn.close()

