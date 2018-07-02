#!/usr/bin/python
# -*- coding:utf8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import time
import datetime
import random
import MySQLdb as mdb

from lxml import etree
from selenium import webdriver
from tqdm import tqdm


class weixin_spider:
    def __init__(self, ):
        self.check = True
        self.ua = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

    

    # 入口函数
    def run(self):
        self.sublist = self.getSubList()
        sublen = len(self.sublist)

        for i in tqdm(range(0,sublen)):
            self.ename =  self.sublist[i][0].strip()
            self.name =  self.sublist[i][1].strip()

            time.sleep(2)  # 时间间隔为2s发送一次抓取请求，防止禁ip
            self.search_url = ("http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=") % (self.name)
            # subcatch 查找1天内的
            # 爬虫伪装头部设置
            self.uachoice = random.choice(self.ua)
            self.headers = {"User-Agent": self.uachoice,"Referer": self.search_url}
            maincontent = self.get_index(self.search_url)

    '''
    获取公众号主页地址
    '''

    def get_index(self, search_url):
        time.sleep(2)

        html = requests.get(search_url, headers=self.headers, verify=False).content
        selector = etree.HTML(html)

        # 提取文本
        # content = selector.xpath('//div[@class="news-box"]/ul/li/div[@class="txt-box"]/h3/a/@href')
        aHref = selector.xpath('//div[@class="txt-box"]/p/a/@href')
        content = selector.xpath('//div[@class="txt-box"]/p[@class="info"]/label/text()')

        for ci in range(len(content)):
            content[ci] = content[ci].encode('utf-8')
            self.ename = self.ename.encode("utf-8")
            if (content[ci] == self.ename):
                print '获取到:' + content[ci] + '地址入口，正在进入...'
                catchUrlIndex = aHref[ci]
                # print catchUrlIndex
                self.get_list(catchUrlIndex)
            else:
                pass

    '''
    获得公众号主页爬取所有文章列表，这里只显示最近10条群发 ，再筛选今天的
    '''

    def get_list(self, catchUrlIndex):
        time.sleep(2)

        # 使用webdriver.PhantomJS
        driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs',
                                     service_args=['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'])
        driver.get(catchUrlIndex)
        article1 = driver.page_source
        selector1 = etree.HTML(article1)


        # 提取文本
        content = selector1.xpath('//div[@class="weui_media_bd"]/p[@class="weui_media_extra_info"]/text()')
        aText = selector1.xpath('//div[@class="weui_media_bd"]/h4/text()')
        # for i in aText:
        #     print(i)
        #
        # sys.exit(0)

        aHref = selector1.xpath('//div[@class="weui_media_bd"]/h4/@hrefs')


        y = datetime.datetime.now().year
        m = datetime.datetime.now().month
        d = datetime.datetime.now().day

        # 每天晚上11点开始爬 存数据库，然后脚本处理
        today = str(y)+'年'+ str(m) + '月'+ str(d-1)+'日'
        # yesterday = "2018年6月30日"

        print('开始获取：'+ today + '的文章')

        if (len(content) ==0):
            #更改爬虫被封状态
            self.upSubStatus()
            sys.exit(0)

        for contenti in (range(len(content))):
            if(today == content[contenti]):
                listUrl = 'https://mp.weixin.qq.com' + aHref[contenti]
                listaText = aText[contenti].encode('utf8').strip().replace(' ','').replace("\n", "")
                print(listaText)
                isexist = self.checkExist(listaText)
                if(isexist):
                    # print listUrl
                    # 插入数据库待采集队列
                    self.insert_save(listUrl,self.name,listaText)
                    self.upSubTime(self.ename)
                else:
                    print('-')
            else:
                print('--')



    def insert_save(self, url,name,listaText):
        self.config = {
             'host': 'host',
            'port': 3306,
            'user': 'user',
            'passwd': 'pwd',
            'db': 'weCatch',
            'charset': 'utf8',
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql = (
                "insert into queue (url,subname,title) values('%s','%s','%s')" %
                (url,name,listaText))
            print(sql)
            cursor.execute(sql)

            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()

    def upSubTime(self, Ename):
        config = {
            'host': 'host',
            'port': 3306,
            'user': 'user',
            'passwd': 'pwd',
            'db': 'weCatch',
            'charset': 'utf8',
        }
        conn = mdb.connect(**config)
        lastTime = time.strftime('%Y-%m-%d')
        cursor = conn.cursor()
        try:
            sql = ("update subscription SET catchTime ='%s'  WHERE subEname = '%s'" % (lastTime, Ename))
            cursor.execute(sql)
            conn.commit()
        except:
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def upSubStatus(self):
        config = {
            'host': 'host',
            'port': 3306,
            'user': 'user',
            'passwd': 'pwd',
            'db': 'weCatch',
            'charset': 'utf8',
        }
        conn = mdb.connect(**config)
        lastTime = time.strftime('%Y-%m-%d')
        cursor = conn.cursor()
        try:
            sql = ("update subStatus SET status =1 ")
            cursor.execute(sql)
            conn.commit()
        except:
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def checkExist(self, title):
        # 检查查到的文章标题是否存在
        self.config = {
            'host': 'host',
            'port': 3306,
            'user': 'user',
            'passwd': 'pwd',
            'db': 'weCatch',
            'charset': 'utf8',
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql = "select id from queue where title ='%s'  " % (title)
            cursor.execute(sql)
            # 如果没有设置自动提交事务，则这里需要手动提交一次
            self.conn.commit()
            temp = cursor.fetchall()
            if (temp):
                return False
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

       def getSubList(self):
        self.config = {
            'host': 'host',
            'port': 3306,
            'user': 'user',
            'passwd': 'pwd',
            'db': 'weCatch',
            'charset': 'utf8',
        }
        self.conn = mdb.connect(**self.config)

        cursor = self.conn.cursor()
        try:
            sql = "select subEname,subName from subscription where status= 1 "
            cursor.execute(sql)
            temp = cursor.fetchall()
            return temp
            self.conn.commit()
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()
        # main


if __name__ == '__main__':
    weixin_spider().run()
