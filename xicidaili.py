#!/usr/bin/python
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
def getproxyfromDB(cour):
   row = cour.fetchone()
   prot, ip, port, flag = row
   #s = ''.join((str(prot), "://", str(ip), ":", str(port)))
   #proxy = {prot: s}
   return (prot, ip, port)

def get_proxy(url, head, cour):
    (prots, ips, ports) = getproxyfromDB(cour)
    s = ''.join((str(prots), "://", str(ips), ":", str(ports)))
    proxy = {prots: s}
    page = requests.get(url=url, headers=head, proxies=proxy, timeout=3)
    print page.status_code

    soup = BeautifulSoup(page.text, 'lxml')
    res_ip = soup.find_all(text=re.compile("^\d+\.\d+\.\d+\.\d+$"))
    res_prot = soup.find_all('td', text=re.compile(r"HTTP"))
    res_port = soup.find_all('td', text=re.compile(r"^\d+$"))

    for ip, port, prot in zip(res_ip, res_port, res_prot):
        yield (ip.string, port.string, prot.string)


def check_proxy(url, head, con, cour):
    for ip,port,prot in get_proxy(url, head, cour):
        protocol = str(prot).lower()
        s = protocol + "://" + str(ip) + ":" + str(port)
        proxy = {protocol: s}
        try:
            req = requests.get(url=url, headers=head, proxies=proxy,timeout=3)
            if req.status_code == 200:
                value = (protocol, str(ip), int(port),1)
                cour.execute('INSERT into proxyspool values(%s,%s,%s,%s)',value)
                con.commit()
                #将数据库的插入异常纳入监控,防止插入时的主键冲突导致for循环终止.
        except Exception:
            pass

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
    coursor.execute("select * from proxyspool where flag = 1")
    check_proxy(url, head, conn, coursor)
    coursor.close()
    conn.close()

