#!/usr/bin/env python
# coding=utf-8

# Author: GuoZheng
# Mail: gzcug2010@gmail.com
# Created Time: Sat 16 Dec 2017 10:58:52 AM CST


import requests

def checkproxy(protc, ip, port):
    """check the proxy whether it is http or https"""
    s = ''.join((str(protc).lower(), "://", str(ip), ":", str(port)))
    proxy = {str(protc).lower():s}
    if str(protc).lower() == 'http':
        try:
            req = requests.get(url=url1, headers=head1, proxies=proxy, timeout=3)
        except requests.exceptions.RequestException:
            return -1
        else:
            if '西刺免费代理' in req.text:
                return req.status_code
            else:
                return -1
    elif str(protc).lower() == 'https':
        try:
            req = requests.get(url=url2, headers=head2, proxies=proxy,timeout=3)
        except requests.exceptions.RequestException:
            return -1
        else:
            if '美团' in req.text:
                return req.status_code
            else:
                return -1
    else:
        return -1

url1 = "http://www.xicidaili.com/nn/"

head1 = { 
    'Host': "www.xicidaili.com",
    'Referer': "http://www.xicidaili.com/nn/",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'Connection': 'keep-alive'
}


url2 = "https://www.meituan.com/"
head2 = {
        'Connection': 'keep-alive',
        'Host': 'www.meituan.com',
        'Referer': 'https://www.meituan.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/62.0.3202.94 Safari/537.36HH=17Runtime=njdjpgffklilbojbobbfecfcgofebbcoALICDN/ DOL/HELLO_GWF_s_382_r2x9ak474125_557'
}


