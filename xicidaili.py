#!/usr/bin/env python
# coding=utf-8

# Author: GuoZheng
# Mail: gzcug2010@gmail.com
# Created Time: Thu 23 Feb 2017 02:23:09 PM CST

from bs4 import BeautifulSoup
import requests
import re
import pymysql as mdb
import checkProxyof
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '910830gz',
    'db': 'proxies',
    'charset': 'utf8'
}
def getproxyfromDB(cour):
   row = cour.fetchone()
   prot, ip, port, flag = row
   #s = ''.join((str(prot), "://", str(ip), ":", str(port)))
   #proxy = {prot: s}
   return (prot, ip, port)

def get_proxy(url, head, cour, num):
    for i in range(num):
        (prots, ips, ports) = getproxyfromDB(cour)
        s = ''.join((str(prots), "://", str(ips), ":", str(ports)))
        proxy = {prots: s}
        try:
            page = requests.get(url=url, headers=head, proxies=proxy, timeout=3)
            if page.status_code == 200 and '西刺免费代理IP' in page.text:
                break
            else:
                continue
        except requests.exceptions.RequestException:
            continue
    else:
        page = requests.get(url=url, headers=head)
    soup = BeautifulSoup(page.text, 'lxml')
    res_ip = soup.find_all(text=re.compile("^\d+\.\d+\.\d+\.\d+$"))
    res_prot = soup.find_all('td', text=re.compile(r"HTTP"))
    res_port = soup.find_all('td', text=re.compile(r"^\d+$"))
    #print(res_ip)
    for ip, port, prot in zip(res_ip, res_port, res_prot):
        yield (ip.string, port.string, prot.string)


def check_proxy(url, head, con, cour, num):
    for ip,port,prot in get_proxy(url, head, cour, num):
        statuscode = checkProxyof.checkproxy(prot, ip, port)
        if statuscode == 200:
            value = (str(prot).lower(), str(ip), int(port),1)
            try:
                cour.execute('INSERT into proxyspool values(%s,%s,%s,%s)',value)
                #将数据库的插入异常纳入监控,防止插入时的主键冲突导致for循环终止.
            except Exception:
                continue

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
    count = coursor.execute("select * from proxyspool where flag = 1 and protocol like 'http'")
    check_proxy(url, head, conn, coursor, count)
    conn.commit()
    coursor.close()
    conn.close()

