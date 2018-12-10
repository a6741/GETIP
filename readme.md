eg:
gp=GETIP()
gp.getip()#获取代理ip
gp.connect(url,headers)#对requests.get的封装 加入代理ip
gp.clearip()#清空当前ip池并重新获取新的代理ip
