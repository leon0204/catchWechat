#!/usr/bin/python
#-*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import time
import re
import os
import ssl
import random

import urllib
import urllib2
from lxml import etree
from lxml import html
from bs4 import BeautifulSoup

from catch_by_urlModel import Model

class weixin_spider:
    def run(self,url,server,uid):
        search_url = url
        
        
        # attention 区分生产和测试环境，存储路径、前缀域名等变量，可以不区分，但是要做出对应配置
        server_path_list = {
            '11': {'path': '/TestFiles/MeiDeNiDevV4/','re_path':'/TestFiles/MeiDeNiDevV4/','ser_name': 'http://imgv4.5imakeup.com/'},
            '2202': {'path': '/statics/Web/Assert', 're_path':'/statics/','ser_name': 'https://v3f.imacco.com/'}
            }

        save_path = server_path_list[server]['path']
        re_path = server_path_list[server]['re_path']
        ser_name = server_path_list[server]['ser_name']

        # 爬虫伪装头部设置
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0","Referer":search_url}
        self.log('开始抓取文章',self.log_path )
        maincontent  = self.get_content(search_url,save_path,ser_name,re_path,uid)


    # 获得输入的url 的详情内容
    def get_content(self, each,save_path,ser_name,re_path,uid):
        data = {}
        article = requests.get(each, headers=self.headers, verify=False).content
        # print article
        soup = BeautifulSoup(article, 'html.parser')  # 文档对象
        selector = etree.HTML(article)
        #

        # 2 作者
        # if(selector.xpath('//*[@id="post-user"]/text()')):
        #     data['user'] = selector.xpath('//*[@id="post-user"]/text()')[0]
        # else:
        #     data['user'] = ''
        # 1 标题
        if (selector.xpath('//*[@id="activity-name"]/text()')):
            data['title'] = selector.xpath('//*[@id="activity-name"]/text()')[0]
        else:
            data['title'] = ''
        data['title'] = data['title'].strip()
        data['description'] = data['title']


        is_exist = True  # self.checkExist(data['title'])



        if(is_exist):  # 判断是否已经抓取过了，不存在为 True

            #  3 发布时间
            data['createtime'] = selector.xpath('//*[@id="post-date"]/text()')[0]

            #  作者昵称
            # data['nickname'] = selector.xpath('//*[@id="img-content"]/div[1]/em[2]/text()')[0]

            # 5.1 原文url
            # data['url'] = each

            data['uid'] = uid
            ## 获取更新 keyno
            getkeynoModel = Model(self.dev, 'InfoDB', 'KeyNO')
            keyno = getkeynoModel.getkeyno()
            InfoKeyNo =  keyno[0]['InfoKeyNo']

            data['keyNo'] = 'Info' + str(int(InfoKeyNo.replace('Info', '')) + 1).zfill(9)
            getkeynoModel.upkeyno(data['keyNo'])

            # 存info
            saveinfoModel = Model(self.dev, 'InfoDB', 'Info')
            saveinfoModel.saveinfoNew(data)

            # 存infoStatic
            saveinfoStaticModel = Model(self.dev, 'InfoDB', 'InfoStatic')
            saveinfoStaticModel.saveinfoStatic(data)
            keyno = data['keyNo']



            # 4 图片

            # 先获取全文，待会儿方便替换图片地址

            imglist  = soup.find_all('img')

            length = len(imglist)
            newlist = []
            for i in range(0,length):
                if(imglist[i].get('data-src')!=None):
                    newlist.insert(1,imglist[i].get('data-src'))
                if (imglist[i].get('src') != None):
                    newlist.insert(1,imglist[i].get('src'))


            body = soup.find_all('div', class_='rich_media_content ')[0]
            body = str(body).replace('data-src', 'src')

            img = ''
            os.umask(0)
            for i in range(len(newlist)):
                print i
                if(newlist[i].encode("UTF-8")   !=''):
                    bodyorpath = newlist[i]
                    newlist[i] = newlist[i].replace('https:','')
                    newlist[i] = newlist[i].replace('http:','')
                    newlist[i] = newlist[i].replace('//','http://')

                    ##1 下载图片
                    print newlist[i]
                    imgpath = str(time.time()) + str(int(random.uniform(10, 20)))   # 用当前时间戳＋一个随机数 保证图片名称唯一性
                    if not os.path.exists( save_path +'/InfoWebUrl/'+keyno ):
                        os.makedirs(save_path +'/InfoWebUrl/'+keyno)
                    print '创建图片文件夹...'
                    newImgPath = save_path +'/InfoWebUrl/'+keyno+ '/' + imgpath + '.jpg'
                    try:
                        urllib.urlretrieve(newlist[i],newImgPath)
                    except:
                        self.log('抓这个路径出错了' +newlist[i] , 'wrongImg')
                        continue
                    print '下载图片资源...'

                    # 2 替换body 的愿路径 和本服务器的路径
                    saveimgpath = newImgPath.replace(re_path,'')
                    body = body.replace(bodyorpath,ser_name +saveimgpath)
                    print '替换抓取页面中原图片路径...'

                    #  加一个insert uploadImg
                    save_img_model = Model(self.dev, 'UploadDB', 'Image')
                    save_img_model.saveImg(keyno,imgpath)
                    img += ser_name +newImgPath


            data['imgurl'] = img

            #5 文章主体部分
            # file_path = data['title']
            file = 'info.html'
            if not os.path.exists(save_path +'/WebUrl/'+keyno):
                os.makedirs(save_path +'/WebUrl/'+keyno)
            with open(save_path + '/WebUrl/' +keyno + '/' + file, 'w') as f:
                f.write(body)
            data['body'] = save_path  + '/' + file

            #  加一个insert uploadInfo.html
            save_url_model = Model(self.dev, 'UploadDB', 'WebUrl')
            save_url_model.saveInfo(keyno, file)

            # print data
            # self.log('suceess : 抓取文章：'+data['title'] +'成功！',self.log_path)

        else:
            self.log('waring : have checked unlink-subscription，catch forwards!',self.log_path)

    def log(self,loginfo,logtype):
        path = '/workspace/django-bash/log/' + logtype

        with open(path, 'w') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + loginfo+'\n')

    def __init__(self, ):
        self.check = True

        self.log_path = 'catch_by_url.log'  # 设置日志 path

        dev_list = {'11': {'server': '192.168.1.11', 'user': 'root', 'pwd': '123456'},
                    '2202': {'server': 'rm-bp1528hy77m556s12.mysql.rds.aliyuncs.com', 'user': 'lokie', 'pwd': 'Kitche931743'}
                    }

        self.dev = dev_list[server]


if __name__ == '__main__':
    print ''''' 
              *********************************************************  
              **        Welcome to Spider of 公众号(采集单个url)       **  
              **         Created on 2017-06--20                      **  
              **          @author: leon.si                           **  
              *********************************************************
      '''

    url = str(sys.argv[1])
    # keyno = str(sys.argv[2])
    server = str(sys.argv[2])
    uid = str(sys.argv[3])

    print url
    print server
    print uid
    weixin_spider().run(url,server,uid)

