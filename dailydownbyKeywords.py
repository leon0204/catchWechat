#!/usr/bin/python
#-*- coding:utf8 -*-

#每天采集数热门关键词 以及对应的公众号更新文章
#这三行代码是防止在python2上面编码错误的，在python3上面不要要这样设置
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from urllib import quote


import requests
import time
import re
import json
import os
import ssl
import random

import urllib
import urllib2
from lxml import etree
from lxml import html

from bs4 import BeautifulSoup

import MySQLdb as mdb

class weixin_spider:
    def __init__(self, ):
        self.check = True


    def getSubList(self):
        # 查询公众号列表
        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'xxxx',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8mb4'
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql = "select subEname,subName from subscription where status= 1 "
            cursor.execute(sql)
            temp = cursor.fetchall()
            return  temp
            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            # 发生错误时会滚
            self.conn.rollback()
        finally:
            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            self.conn.close()

    #入口函数
    def run(self):
        # self.sublist = self.getSubList()
        # for self.ename, self.name in self.sublist:
        self.search_url = "http://weixin.sogou.com/"
        # 爬虫伪装头部设置
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0","Referer": self.search_url}
        self.log('开始抓取主页热词列表........')
        res = self.get_list(self.search_url)
        self.log('抓取主页热词列表成功！：')
        #先将昨天的排行列表文章全部删除 软删除
        self.remove()
        for x in  res['keyword']:
            print x
        for i in range(0,10):
            #抓取热词对应的具体文章：
            self.get_keylist(res['keyurl'][i],i)
        self.log('抓取今日热门文章结束')

    # 获得公众号文章详情页列表
    def get_keylist(self, search_url,i):

        html = requests.get(search_url, headers=self.headers, verify=False).content
        selector = etree.HTML(html)
        # 提取文本
        content = selector.xpath('//div[@class="news-box"]/ul/li/div[@class="txt-box"]/h3/a/@href')
        for list in content:
            maincontent = self.get_content(list,i)





    # 获得本日热点关键词数据
    def get_list(self, search_url):
        data = {}
        # keylist =  [0] * 5
        data['table_name'] = 'dailyKeyword'
        html = requests.get(search_url, headers=self.headers, verify=False).content
        selector = etree.HTML(html)

        # 提取文本
        keyurl = selector.xpath('//div[@class="aside"]/ol[@class="hot-news"]/li/a/@href')
        keyword = selector.xpath('//div[@class="aside"]/ol[@class="hot-news"]/li/a/text()')
        res = {}
        res['keyurl'] = keyurl
        res['keyword'] = keyword

        for x in range(0,10):
            data['keyword'] = keyword[x]
            data ['keyurl'] = keyurl[x]
            data ['id'] = (x+1)
            self.save(data)
        return res



    # 获得热词详情
    def get_content(self, each,i):
        data = {}
        article = requests.get(each, headers=self.headers, verify=False).content

        soup = BeautifulSoup(article, 'html.parser')  # 文档对象
        selector = etree.HTML(article)
        #
        # data['rank'] = self.rank.replace('rank','')
        data['rank'] = (i+1)
        # 2 作者
        if(selector.xpath('//*[@id="post-user"]/text()')):
            data['user'] = selector.xpath('//*[@id="post-user"]/text()')[0]
        else:
            data['user'] = ''
        # 1 标题
        if (selector.xpath('//*[@id="activity-name"]/text()')):
            data['title'] = selector.xpath('//*[@id="activity-name"]/text()')[0]
        else:
            data['title'] = ''
        data['title'] = data['title'].strip()

        # checkrelate = self.checkRelate(data['user'])
        # print 'user:' + data['user'] + 'name:' + self.name
        # checkrelate = (False,True)[data['user'] == self.name]
        data['table_name'] = 'daily'
        isexist = self.checkExist(data)

        if(isexist):#判断文章是否存在

            #3 发布时间
            data['createtime'] = selector.xpath('//*[@id="post-date"]/text()')[0]

            #作者昵称
            # data['nickname'] = selector.xpath('//*[@id="img-content"]/div[1]/em[2]/text()')[0]

            # 5.1 原文url
            data['url'] = each

            # 4 图片

            #先获取全文，待会儿方便替换图片地址
            body = soup.find_all('div', class_='rich_media_content ')[0]
            body = str(body).replace('data-src', 'src')


            imgurl = selector.xpath('//*[@id="js_content"]/p/img/@data-src')
            imgSpan = selector.xpath('//*[@id="js_content"]/p/span/img/@data-src')
            imgEmSpan = selector.xpath('//*[@id="js_content"]/p/em/span/img/@data-src')
            imgStrongSpan = selector.xpath('//*[@id="js_content"]/p/strong/span/img/@data-src')
            imgStrongSpanStrongSpan = selector.xpath('//*[@id="js_content"]/p/strong/span/strong/span/img/@data-src')
            imgTotal = imgurl + imgSpan + imgEmSpan + imgStrongSpan + imgStrongSpanStrongSpan

            img = ''
            for i in range(len(imgTotal)):
                ##1 下载图片
                imgpath = str(time.time()) + str(int(random.uniform(10, 20)))   # 用当前时间戳＋一个随机数 保证图片名称唯一性
                if not os.path.exists('/home/wwwroot/laravel/public/img/daily/' + data['user']):
                    os.makedirs('/home/wwwroot/laravel/public/img/daily/' + data['user'], mode=0755)
                newImgPath = '/home/wwwroot/laravel/public/img/daily/' + data['user'] + '/' + imgpath + '.jpg'
                urllib.urlretrieve(imgTotal[i],newImgPath)

                # 2 替换body 的愿路径 和本服务器的路径
                saveimgpath = newImgPath.replace('/home/wwwroot/laravel/public','')
                body = body.replace(imgTotal[i],'http://leon0204.com'+saveimgpath)

                img += 'http://leon0204.com'+newImgPath
            data['imgurl'] = img

            #5 文章主体部分
            file_path = data['title']
            file = file_path.replace('/', '-')
            if not os.path.exists('/home/wwwroot/url/daily/' + data['user']):
                os.makedirs('/home/wwwroot/url/daily/' + data['user'], mode=0755)
            with open('/home/wwwroot/url/daily/' + data['user'] + '/' + file, 'w') as f:
                f.write(body)
            data['body'] = '/home/wwwroot/url/daily/' + data['user'] + '/' + file



            #6 信息处理状态： 0 未处理  1 图片已经转储到本地 2 已经发布到线上待处理数据库
            data['status'] = 0

            self.log('suceess : 抓取文章：'+data['title'] +'成功！' )
            ##存储
            self.saveInfo(data)
        else:
            self.log('waring : have checked unlink-subscription，catch forwards!')



    def save(self,data):
        #保存每天的key 排行版
        # 连接数据库

        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'xxxx',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8mb4'
        }
        self.conn = mdb.connect(**self.config)
        tb = data['table_name']
        cursor = self.conn.cursor()
        try:
            sql = (
            "update %s SET keyword ='%s',keyurl = '%s' WHERE id = %s" %(tb,data['keyword'],data['keyurl'],data['id'])
            )

            cursor.execute(sql)


            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            # 发生错误时会滚
            self.conn.rollback()
        finally:
            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            self.conn.close()

    def remove(self):
        #删除昨天的文章，软删除status 变为1
        # 连接数据库

        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'xxxx',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8mb4'
        }
        self.conn = mdb.connect(**self.config)
        cursor = self.conn.cursor()
        try:
            sql = (
            "update daily SET status =1"
            )

            cursor.execute(sql)


            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            # 发生错误时会滚
            self.conn.rollback()
        finally:
            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            self.conn.close()


    def checkExist(self,data):
        #检查查到的文章标题是否存在
        #连接数据库

        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'xxxx',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8mb4'
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql ="select id from %s where title ='%s'  " %(data['table_name'],data['title'])
            cursor.execute(sql)
            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
            temp = cursor.fetchall()
            if (temp):
                return  False
            else:
                return True
        except:
            import traceback
            traceback.print_exc()
            # 发生错误时会滚
            self.conn.rollback()
        finally:

            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            self.conn.close()


    #存储文章
    def saveInfo(self,data):
        # 连接数据库

        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'xxxx',
            'passwd': 'xxxx',
            'db': 'xxxx',
            'charset': 'utf8mb4'
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql = (
            "insert into %s (title, user, createtime, body, status,url,imgurl,rank) values('%s', '%s', '%s','%s', '%s', '%s', '%s','%s')" %
            (data['table_name'],data['title'],data['user'],data['createtime'],data['body'],data['status'],data['url'],data['imgurl'],data['rank']))
            cursor.execute(sql)


            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            # 发生错误时会滚
            self.conn.rollback()
        finally:
            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            self.conn.close()



    def log(self,msg):
        # print u'%s: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg) 用新的 不提示日期的
        print msg





    # main
if __name__ == '__main__':
    weixin_spider().run()
