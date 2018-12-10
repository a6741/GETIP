#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 21:13:10 2018

@author: ljk
"""
#因为过度频繁访问被蘑菇街ban了。。。。。所以设置ip代理
import redis
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import execjs
import threading
class GETIP:
    def __init__(self,host='localhost',password='',port=6379, decode_responses=True,testurl='',banword=''):
        self.host=host
        self.password=password
        self.port=port
        self.decode_responses=decode_responses
        self.testurl=testurl
        self.banword=banword
        redi=self.dbconnect()
        redi.set('ipflag','1')
        pass
    def choseip(self,wait=True):
        redi=self.dbconnect()
        num=redi.scard('ips')
        if not wait and num<2:
            return 0
        got=True
        while got:
                try:
                    proxy=redi.srandmember('ips')
                    len(proxy)
                    got=False
                except:
                    if wait:
                        pass
                    else:
                        return 0
        k={'http': 'http://{ip}','https': 'https://{ip}'}
        k['http']=k['http'].format(ip=proxy)
        k['https']=k['https'].format(ip=proxy)
        return k
    def clearip(self):
        redi=self.dbconnect()
        redi.delete('ips')
        self.getip()
    def connect(self,url,headers,firstur=False,timeouttry=1):#从数据库ip池获取代理ip
        req=''
        fla=True
        filtstring=self.banword
        try:
            if firstur:
                req=requests.get(url=url,headers=headers)
                if filtstring not in req.text or filtstring=='' and req.status_code==200:
                    fla=False
        except:
            pass
        firstur=False
        while fla:
            k=self.choseip()
            if 'https' in url:
                k.pop('http')
            try:
                fla=False
                req=requests.get(url=url,headers=headers,proxies=k,timeout=3)
                fla=True
                if req.status_code!=200 or (filtstring in req.text and filtstring!=''):
                        fla=True
                else:
                    fla=True
            except:
                fla=True
                k=self.choseip()
        return req
    def return_cookie(self,url):
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',}
        first_html = requests.get(url=url,headers=headers).content.decode('utf-8')
        js_string = ''.join(re.findall(r'(function .*?)</script>', first_html))
        js_arg = ''.join(re.findall(r'setTimeout\(\"\D+\((\d+)\)\"', first_html))
        js_name = re.findall(r'function (\w+)',js_string)[0]
        js_string = js_string.replace('eval("qo=eval;qo(po);")', 'return po')
        func = execjs.compile(js_string)
        string=func.call(js_name,js_arg)
        string = string.replace("document.cookie='", "")
        return string
    def dbconnect(self):
        redi=redis.Redis(host=self.host, port=self.port, decode_responses=self.decode_responses,password=self.password)
        return redi
    def testip(self,proxy):#测试代理ip是否可用
            redi=self.dbconnect()
            headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
            url="https://www.ip.cn/"
            url='http://pv.sohu.com/cityjson'
            try:
                k={'http': 'http://{ip}','https': 'https://{ip}'}
                k['http']=k['http'].format(ip=proxy)
                k['https']=k['https'].format(ip=proxy)
                res = requests.get(url,proxies=k,headers=headers,timeout=10)
                so=BeautifulSoup(res.text,'lxml')
                #print(so.text)
                if proxy.split(':')[0] in so.text:
                    if self.testurl!='':
                        try:
                            url='https://shop.mogujie.com/detail/1m6b82m'
                            h2={
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'__mgjuuid=64b224ec-0db4-483e-b5b7-5a662b2dfa5f; _mwp_h5_token_enc=830209ef9f3a3232dcc9936f4f531a6f; _mwp_h5_token=4f13275f086631f3136196c979c43e8f_1542268893610',
                'Host':'shop.mogujie.com',
                'Referer':'https://list.mogujie.com/s?q=%E5%A5%B3%E8%A1%AC%E8%A1%AB&ppath=&sort=sell&ptp=1.5y18ub.0_sortList.2.XwM8Ikc9',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
                                }
                            k={'http': 'http://{ip}','https': 'https://{ip}'}
                            k['http']=k['http'].format(ip=proxy)
                            k['https']=k['https'].format(ip=proxy)
                            req=requests.get(url,proxies=k,headers=h2,timeout=5)
                            if self.banword not in req.text:
                                check=redi.sismember('ips',str(proxy).replace("'",""))
                                if not check:
                                    redi.sadd('ips',str(proxy).replace("'",""))
                                    print(proxy)
                            req.close()
                        except:
                            return 0
                    else:
                        check=redi.sismember('ips',str(proxy).replace("'",""))
                        if not check:
                            redi.sadd('ips',str(proxy).replace("'",""))
                            print(proxy)
                        return 1
                else:
                    return 0
            except:
                return 0
    def ooget(self):
        headers={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection':'keep-alive',
        'Cookie':'yd_cookie=02b526c0-bb6e-4ad5c82f2364326dda550f506e5c004d1adc',
        'Host':'www.89ip.cn',
        'Referer':'http://www.89ip.cn/ti.html',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        }
        url='http://www.89ip.cn/tqdl.html?num={num}&address=&kill_address=&port=&kill_port=&isp='
        url=url.format(num=100)
        print(url)
        rr=[]
        try:
            proxy=self.choseip(wait=False)
            proxy['https']
            qq=requests.get(url,headers=headers,proxies=proxy,timeout=3)
        except:
            qq=requests.get(url,headers=headers)
        rr=re.findall('\d+.\d+.\d+.\d+:\d+',qq.text)
        if  len(rr)==0:
            self.anotherget()
            return
        ttt=[]
        print('check')
        for r in rr:
            t=threading.Thread(target=self.testip,args=(r,))
            t.setDaemon(False)
            t.start()
            ttt.append(t)
        for t in ttt:
            t.join()
    def anotherget(self):
        url='http://www.66ip.cn/nmtq.php?getnum={num}&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=0&proxytype=1&api=66ip'
        url=url.format(num=50)
        headers={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection':'keep-alive',
        'Cookie':self.return_cookie(url),
        'Host':'www.66ip.cn',
        'Referer':'http://www.66ip.cn/nm.html',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        }
        print(url)
        rr=[]
        try:
            proxy=self.choseip(wait=False)
            proxy['https']
            qq=requests.get(url,headers=headers,proxies=proxy,timeout=3)
        except:
            qq=requests.get(url,headers=headers)
        rr=re.findall('\d+.\d+.\d+.\d+:\d+',qq.text)
        if  len(rr)==0:
            self.ooget()
            return
        ttt=[]
        print('check')
        for r in rr:
            t=threading.Thread(target=self.testip,args=(r,))
            t.setDaemon(False)
            t.start()
            ttt.append(t)
        for t in ttt:
            t.join()
    def getip(self):
        rd=random.randint(1,20)
        if rd<7:
            self.anotherget()
        elif rd<14:
            self.ooget()
        else:
            #self.ooget()
            if self.onegetip()==0:
                self.ooget()
    def onegetip(self):#从ip代理网站获取ip
        headers={
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive",
    "Cookie":"_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWYwNDBiMjNlZDNkMWU5MTMzZTllODhiYTcxZWZmMDQ4BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUMraTBQclNKN0VjTXNUVnBIQmhFV09sNk1MUWFlWU5Qb1NzS3JOd2oxaXM9BjsARg%3D%3D--03cfdc3029f7ab0bfdddc79973642fe22c7f746b",
    "Host":"www.xicidaili.com",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                }
        proxys=[]
        ttt=[]
        n=1

        while(n<5):
            tryt=0
            url = 'http://www.xicidaili.com/nn/'+str(n)
            shtml=requests.get(url,headers=headers)
            while shtml.status_code!=200:
                try:
                    shtml.close()
                    tryt+=1
                    if tryt>3:
                        return 0
                    proxy=self.choseip(wait=False)
                    shtml=requests.get(url,headers=headers,proxies=proxy)
                except:
                    pass
            Soup=BeautifulSoup(shtml.text,'lxml')
            theurl=Soup.find_all('tr',class_="odd")
            for ur in theurl:
                proxys.append(ur.find_all('td')[1].get_text()+":"+ur.find_all('td')[2].get_text())
            for proxy in proxys:
                t=threading.Thread(target=self.testip,args=(proxy,))
                t.setDaemon(False)
                t.start()
                ttt.append(t)
            shtml.close()
            print(n)
            n+=1
        for t in ttt:
            t.join()
        return 1