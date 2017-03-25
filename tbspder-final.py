# coding=utf-8
import urllib
from urllib import quote

import MySQLdb
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import os
import sqlite3
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def itemread(keyword):

    path=u'淘宝图片'
    ukeyword=unicode(keyword, "utf-8")

    s='1'
    isExist=False
    # driver = webdriver.PhantomJS(executable_path='C:\phantomjs.exe')
    driver = webdriver.PhantomJS()
    driver.implicitly_wait(10)
    # file = open(uipath, 'a')
    # filenew = open(uipathnew, 'w')
    sql=[]
    pic=[]
    img=[]
    try:
        newfolder1 = 'D:\\' + path.encode("gb2312")
        newfolder2 = 'D:\\' + path.encode("gb2312") + '\\' + ukeyword.encode("gb2312")
        if not os.path.exists(newfolder1):
            os.mkdir(newfolder1)
            os.mkdir(newfolder2)
        else:
            if not os.path.exists(newfolder2):
                os.mkdir(newfolder2)

        conn = MySQLdb.connect(host='localhost', user='olfzpp', passwd='1234abcd', db='items',charset='utf8')
        print 'ok connected.'
        # 所有的查询，都在连接con的一个模块cursor上面运行的
        cur = conn.cursor()
        cur.execute('select nid from taobao')
        data = cur.fetchall()
        # SQL 插入语句
        while(True):
            # print '进入循环'
            driver.get("https://s.taobao.com/search?q=" + quote(keyword) + '&s=' + str(s))
            print "开始访问：https://s.taobao.com/search?q=" + quote(keyword) + '&s=' + str(s)
            # print '等待开始 寻找 "class=help"………………'
            WebDriverWait(driver,30, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "help")))
            # print '发现 "class=help"  等待结束'
            # print driver.page_source
            bs = BeautifulSoup(driver.page_source)  # 把selenium的webdriver调用page_source函数在传入BeautifulSoup中，就可以用BeautifulSoup解析网页了
            for link in bs.find_all('a', attrs={"class": "pic-link J_ClickStat J_ItemPicA"}):
                #由于在<a ....>中还存在<img >,其中我们需要的data-src以及alt属性都在这个img标签内，在这里我们使用link.find('img').get(attrs)来进行内嵌img层的搜索
                #print type(link)
                imgtag=link.find('img')
                # print imgtag.attrs
                img_src = 'https:'+imgtag['data-src'] #商品图片
                name = imgtag['alt'].replace('\\','') #商品中文名
                nid=link['data-nid'] #商品编号
                detail = 'http:'+link['href'].replace('\\','')  # 商品链接
                # print img_src,name,nid,detail
                # for line in open(uipath):
                for line in list(data):
                    if (line[0].find(nid)>-1):
                        isExist=True
                        print '已有相同item不再录入',name
                        break
                if(not isExist):
                    picname = newfolder2 + '\\' + nid + '.jpg'
                    pic.append([img_src,picname])
                    sql.append('INSERT INTO TAOBAO(NID,KEYWORD,NAME,PRICE,IMAGE,URL) VALUES ("' + nid + '","'+keyword+ '","' + str(name.encode('utf-8')) + '","' + link['trace-price'] + '","' +str(img_src) + '","' + detail + '")')
                    # print 'INSERT INTO TAOBAO(NID,NAME,PRICE,IMAGE,URL) VALUES ("' + nid + '","' + str(name.encode('utf-8')) + '","' + link['trace-price'] + '","' +str(img_src) + '","' +",https:" + detail + '")'
                    # file.writelines(nid + "," + str(name.encode('utf-8')) + ",https:" + str(img_src) + "," + str(
                    #     link['trace-price'] + ",https:" + detail) + '\n')
                    print '成功录入新增商品', name
                    #录入商品链接改为录入商品图片str(img_src)本地地址picname
                    sql.append('INSERT INTO TAOBAONEW(NID,KEYWORD,NAME,PRICE,IMAGE,URL) VALUES ("' + nid + '","' +keyword+ '","' +str(
                        name.encode('utf-8')) + '","' + link['trace-price'] + '","' +picname + '","' +  detail + '")')
                    #下载图片
                    # picname = newfolder2 + '\\' +str(name.encode('utf-8'))+'.jpg'

                    # print '======>INSERT INTO TAOBAO(NID,NAME,PRICE,IMAGE,URL) VALUES ("' + nid + '","' + str(
                    #     name.encode('utf-8')) + '","' + link['trace-price'] + '","' + str(
                    #     img_src) + '","' + ",https:" + detail + '")'
                    # filenew.writelines(nid + "," + str(name.encode('utf-8')) + ",https:" + str(img_src) + "," + str(
                    #      link['trace-price'] + ",https:" + detail) + '\n')
            if(bs.find('span',attrs={"class":"icon icon-btn-next-2-disable"})!=None):
                print '发现下一页不可读'
                break
            else:
                print '下一页可读'

                for n in bs.find_all('a', attrs={"class": "J_Ajax num icon-tag"}):
                    # print '找到了以下J_Ajax num icon-tag元素:'
                    # print n
                    if(n['trace'].find('down')>0):
                        # print '发现了关键字down'
                        s=int(n['data-value'])+1
        for s in sql:
            try:
                cur.execute(s)
                # 提交到数据库执行
                conn.commit()
            except Exception,e:
                print e
                continue
            print '成功执行SQL语句==>'+s
        for p in pic:
            print p[0],p[1]
            try:
                urllib.urlretrieve(p[0], p[1])
            except Exception,e:
                print e
                continue
            print '成功下载图片' + p[1]
        print '成功下载所有图片'
    except Exception, e:
        print e
    finally:
        if conn:
            # 无论如何，连接记得关闭
            conn.close()
    # file.close()


if __name__ == '__main__':

    word = ''
    itemread(word)