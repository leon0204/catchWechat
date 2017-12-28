#!/usr/bin/python
#-*- coding:utf8 -*-
#这三行代码是防止在python2上面编码错误的，在python3上面不要要这样设置
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



import time
import os
import random

import requests
import urllib
from urllib import quote
from lxml import etree
from lxml import html
from bs4 import BeautifulSoup

import MySQLdb as mdb

class weixin_spider:
    def __init__(self, ):
        self.check = True
        
    def run(self):
        self.sublist = self.getSubList()
        for self.ename, self.name in self.sublist:
            self.search_url = ("http://weixin.sogou.com/weixin?usip=&query=%s&ft=&tsn=1&et=&interation=&type=2&wxid=&page=1&ie=utf8") %(self.ename)
            self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0","Referer": self.search_url}
            self.log('开始抓取公众号[' + self.name + ']' + time.strftime('%Y-%m-%d') + '的文章'   +':')
            maincontent = self.get_list(self.search_url)

    def get_list(self, search_url):
        html = requests.get(search_url, headers=self.headers, verify=False).content
        selector = etree.HTML(html)
        # 提取文本
        content = selector.xpath('//div[@class="news-box"]/ul/li/div[@class="txt-box"]/h3/a/@href')
        for list in content:
            maincontent = self.get_content(list)

    # 获得公众号文章列表详情内容
    def get_content(self, each):
        data = {}
        article = requests.get(each, headers=self.headers, verify=False).content
        soup = BeautifulSoup(article, 'html.parser')
        selector = etree.HTML(article)
 
        if(selector.xpath('//*[@id="post-user"]/text()')):
            data['user'] = selector.xpath('//*[@id="post-user"]/text()')[0]
        else:
            data['user'] = ''
            
        if (selector.xpath('//*[@id="activity-name"]/text()')):
            data['title'] = selector.xpath('//*[@id="activity-name"]/text()')[0]
        else:
            data['title'] = ''
        data['title'] = data['title'].strip()

        checkrelate = self.checkRelate(data['user'])
        print 'user:' + data['user'] + 'name:' + self.name
        # checkrelate = (False,True)[data['user'] == self.name]
        isexist = self.checkExist(data['title'])

        if(checkrelate and isexist):#判断是否是目标公众号

            data['createtime'] = selector.xpath('//*[@id="post-date"]/text()')[0]

            #作者昵称
            # data['nickname'] = selector.xpath('//*[@id="img-content"]/div[1]/em[2]/text()')[0]
            
            data['url'] = each

            # 图片
            imglist = soup.find_all('img')
            length = len(imglist)
            newlist = []
            for i in range(0, length):
                if (imglist[i].get('data-src') != None):
                    newlist.insert(1, imglist[i].get('data-src'))
                if (imglist[i].get('src') != None):
                    newlist.insert(1, imglist[i].get('src'))
            body = soup.find_all('div', class_='rich_media_content ')[0]
            body = str(body).replace('data-src', 'src')
            img = ''
            for i in range(len(newlist)):
                print i
                if (newlist[i].encode("UTF-8") != ''):
                    tempBody = newlist[i]
                    newlist[i] = newlist[i].replace('https:','')
                    newlist[i] = newlist[i].replace('http:','')
                    newlist[i] = newlist[i].replace('//','http://')
                    
                    imgpath = str(time.time()) + str(int(random.uniform(10, 20)))
                    if not os.path.exists('/home/wwwroot/laravel/public/img/weixin/' + data['user']):
                        os.makedirs('/home/wwwroot/laravel/public/img/weixin/' + data['user'], mode=0755)
                    newImgPath = '/home/wwwroot/laravel/public/img/weixin/' + data['user'] + '/' + imgpath + '.jpg'
                    urllib.urlretrieve(newlist[i], newImgPath)
                    
                    saveimgpath = newImgPath.replace('/home/wwwroot/laravel/public', '')
                    body = body.replace(tempBody, 'https://www.leon0204.com' + saveimgpath)
                    
                    img += 'https://www.leon0204.com' + newImgPath
            data['imgurl'] = img
            
            # 文章主体部分
            file_path = data['title']
            file = file_path.replace('/', '-')
            if not os.path.exists('/home/wwwroot/url/weixin/' + data['user']):
                os.makedirs('/home/wwwroot/url/weixin/' + data['user'], mode=0755)
            with open('/home/wwwroot/url/weixin/' + data['user'] + '/' + file, 'w') as f:
                f.write(body)
            data['body'] = '/home/wwwroot/url/weixin/' + data['user'] + '/' + file

            # 信息处理状态： 0 未处理  1 图片已经转储到本地 2 已经发布到线上待处理数据库
            data['status'] = 0
            data['userEname'] = self.getuserEname(data['user'])
            self.log('suceess : 抓取文章：'+data['title'] +'成功！' )
            ##存储
            self.save(data)
        else:
            self.log('waring : have checked unlink-subscription，catch forwards!')


# Model ()
# host,port,user,passwd,db 配置成自己的 Mysql 配置
# 实际使用可以考虑把model层封装成包import使用，这里为了方便环境搭建没有做

    def save(self,data):
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': 'xxx',
            'db': 'xxx',
            'charset': 'utf8'
        }
        self.conn = mdb.connect(**self.config)
        cursor = self.conn.cursor()
        try:
            sql = (
            "insert into Article (title, user, userEname,createtime, body, status,url,imgurl) values('%s','%s', '%s', '%s','%s', '%s', '%s', '%s')" %
            (data['title'],data['user'],data['userEname'],data['createtime'],data['body'],data['status'],data['url'],data['imgurl']))
            cursor.execute(sql)
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()
            
        
    def checkRelate(self,subName):
        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'passwd': 'xxxx',
            'db': 'xxx',
            'charset': 'utf8'
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql ="select subName from subscription where status= 1 and subName ='%s'  " %(subName)
            cursor.execute(sql)
            self.conn.commit()
            temp = cursor.fetchall()
            if (temp):
                return True
            else:
                return False
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()


    def checkExist(self,title):
        #检查查到的文章标题是否存在
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8'
        }
        self.conn = mdb.connect(**self.config)
        cursor = self.conn.cursor()
        try:
            sql ="select id from Article where title ='%s'  " %(title)
            cursor.execute(sql)
            self.conn.commit()
            temp = cursor.fetchall()
            if (temp):
                return False
            else:
                return True
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()

    def getuserEname(self,user):
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8'
        }
        self.conn = mdb.connect(**self.config)
        cursor = self.conn.cursor()
        try:
            sql ="select id from subscription where subName ='%s'  " %(user)
            cursor.execute(sql)
            self.conn.commit()
            temp = cursor.fetchall()
            return temp
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()

    def getSubList(self):
        # 查询公众号列表
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': 'xxxx',
            'db': 'xxx',
            'charset': 'utf8'
        }
        self.conn = mdb.connect(**self.config)
        cursor = self.conn.cursor()
        try:
            sql = "select subEname,subName from Subscription where status= 1 "
            cursor.execute(sql)
            temp = cursor.fetchall()
            return  temp
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()


    def get_search_result_by_keywords(self):
        self.log('搜索地址为：%s' % self.sogou_search_url)
        return self.s.get(self.sogou_search_url, headers=self.headers, timeout=self.timeout).content


    def log(self,msg):
        # print u'%s: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg) 
        print msg


if __name__ == '__main__':
    print ''''' 
              *****************************************  
              **    Welcome to Spider of 公众号爬虫       **  
              **      Created on 2017-08--20          **  
              **      @author: leon.si         **  
              ***************************************** 
      '''

    # subscription = raw_input(u'输入要爬取的公众号')
    # if not subscription:
    #     subscription = 'Article'
    weixin_spider().run()

