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
import threading
class GETIP:
    def __init__(self,host='localhost',password='',port=6379, decode_responses=True):
        self.host=host
        self.password=password
        self.port=port
        self.decode_responses=decode_responses
        redi=self.dbconnect()
        redi.set('ipflag','1')
        pass
    def connect(self,url,headers,firstur=False,filtstring='很抱歉，由于您访问的频率过高有可能对网站造成安全威胁，您的访问被阻断。',timeouttry=3):#从数据库ip池获取代理ip
        redi=self.dbconnect()
        got=True
        while got:
            try:
                proxy=redi.srandmember('ips')
                len(proxy)
                got=False
            except:
                time.sleep(random.randint(0,5))
                if redi.get('ipflag')=='1':
                    redi.set('ipflag','0')
                    self.getip()
                    redi.set('ipflag','1')
                else:
                    pass
        k={'http': 'http://{ip}','https': 'https://{ip}'}
        k['http']=k['http'].format(ip=proxy)
        k['https']=k['https'].format(ip=proxy)
        req=''
        fla=True
        tryt=0
        #print('ojbkojbk')
        while fla:
            try:
                if firstur:
                        req=requests.get(url=url,headers=headers)
                        if filtstring in req.text and filtstring!='':
                            req=requests.get(url=url,headers=headers,proxies=k,timeout=5)
                        if filtstring in req.text and filtstring!='':
                            tryt=timeouttry+2
                            1/0
                else:
                    req=requests.get(url=url,headers=headers,proxies=k,timeout=5)
                    if filtstring in req.text and filtstring!='':
                        tryt=timeouttry+2
                        1/0
                    #print('uk')
                fla=False
            except:
                #print('233333')
                tryt+=1
                if tryt>timeouttry:
                    try:
                        redi.srem('ips',proxy)
                    except:
                        pass
                    fla=False
                    req=self.connect(headers,url)
        return req
    def dbconnect(self):
        redi=redis.Redis(host=self.host, port=self.port, decode_responses=self.decode_responses,password=self.password)
        return redi
    def testip(self,myids,proxy):#测试代理ip是否可用
        #global ips
        #if len(ips)<5:
            redi=self.dbconnect()
            headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}
            #url = "http://ip.chinaz.com/getip.aspx"
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
                    
                    check=redi.sismember('ips',str(proxy).replace("'",""))
                    if not check:
                        redi.sadd('ips',str(proxy).replace("'",""))
                        print(proxy)
                        res.close()
            except:
                pass
    def getip(self):#从ip代理网站获取ip
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
        global proxys
        proxys=[]
        ttt=[]
        n=1
        url = "http://ip.chinaz.com/getip.aspx"
        url="https://www.ip.cn/"
        res = requests.get(url)
        myid=BeautifulSoup(res.text,'lxml')
        idm=re.findall("\d+",myid.text)
        myids='.'.join(idm[:4])
        while(n<5):
            url = 'http://www.xicidaili.com/nn/'+str(n)
            shtml=requests.get(url,headers=headers)
            Soup=BeautifulSoup(shtml.text,'lxml')
            if 'block' in Soup:
                #time.sleep(3600)
                print('You are blocked')
                return
            theurl=Soup.find_all('tr',class_="odd")
            for ur in theurl:
                proxys.append(ur.find_all('td')[1].get_text()+":"+ur.find_all('td')[2].get_text())
            for proxy in proxys:
                t=threading.Thread(target=self.testip,args=(myids,proxy,))
                t.setDaemon(False)
                t.start()
                ttt.append(t)
            print(n)
            n+=1
        for t in ttt:
            t.join()