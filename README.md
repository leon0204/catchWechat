# CatchWechat
抓取微信公众号文章 （仅用做学习交流用途！！！）

pre：
   没有用框架，直接clone 就可以用 
   
基于 python 2.7 。使用3的话，根据 error 自行替换一下包即可


 - `catch_allList.py` ： 抓取 单个指定公众号url  😄 
 
 
 延伸：
 - `dailydown.py` ： 抓取配置的公众号列表，每日发布的文章列表  ✌️
 
## 环境依赖


####  安装 pip
```
wget --no-check-certificate https://github.com/pypa/pip/archive/1.5.5.tar.gz 
tar zvxf 1.5.5.tar.gz    
cd pip-1.5.5/
python setup.py install
pip install --upgrade pip
```

####  使用到的 pip 模块
```
pip install requests
pip install lxml
pip install BeautifulSoup


# Ubantu
apt-get install libmysqld-dev
easy_install MySQL-python

# Centos
yum install python-devel
yum install mysql-devel

```

#### 安装 PhantomJS、selenium

```
pip install selenium

# 安装phantomjs 如果压缩包被墙，可以fq下载之后，再传到服务器，解压获得可执行文件路径，引入项目使用
http://phantomjs.org/download.html
wget -O phantomjs-2.1.1-linux-x86_64.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2


# 使用webdriver.PhantomJS 抓取渲染后的Html
driver = webdriver.PhantomJS(executable_path='这里按各个系统写pha-js的执行路径',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=tlsv1'])
driver.get(each)
page_source =  driver.page_source
```

## 开始使用

####  获取代码
```
cd /home/wwwroot
git clone https://github.com/leon0204/catchWecaht.git
```

#### 导入模板数据库，先创建 `weixin` 数据库 `utf8mb4`
```	
cd catchWecaht
mysql -uroot -p weixin < ./weixin.sql
```

>抓取公众号的列表在 `weixin` 数据库的 `subscription` 表中 


配置所需要用到的库，没有的用 `pip` 基本都可以满足



#### 抓取公众号今日更新列表
```
// 需要设置一下 dailydown.py 中的数据库设置
python dailydown.py
```
数据会存在 `subcatch` 表中 


## 优化和注意事项

#### 优化
1 资源删除，热点抓取bug 修复

`TODO` :
1. ~~dailyKeyword 采集热点关键词时，空数据时候插入，没数据是不会插入，没有写插入语句~~
2. ~~图片采集的优化 ~~
3. 添加TDK 

#### 更新 v1
1. 优化图片采集规则，更全面抓取图片 
2. 修复一些bug

#### 更新 v2
添加 phantomjs 支持 抓取 js 渲染页面

#### 更新 v3
更新 dailydown.py 脚本 ，获取配置的公众号列表每日发布的所有文章列表


#### 更新 v4 （18.7.2）
1. 使用爬虫的时候，注意 time.sleep()， 不然很容易被封禁 。
2. 要用 phantomjs 的要控制一下 selenium版本，在se3之后就不支持了。需要替换成chrome/firefox的noheader模式。
3. 另外搜狗这边好像会默认封禁phantomjs ，如果在客户端开发爬虫的，那很简单，可以通过浏览器访问页面来简单的解封，服务端的话，则需要对验证码图片获取，解码，模拟填入解封。虽然说 pyaccestor 等包可以获取图片验证码，但是成功率堪忧，如果要加上机器学习训练识别模型，无论从机器配置需求还是业务成本来看，复杂度都大大提高了，我的解决办法是：尽量想办法绕过验证码，具体的大家可以自己发挥 😊





- 如果对你有帮助的话， 右上角 Star✨ 鼓励一下，谢谢！
- 欢迎 PR 讨论～ 
- 个人wechat ：leon0204 

