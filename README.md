# CatchWecaht
抓取微信公众号文章

pre：
   没有用框架，直接clone 就可以用，采集文章是 `dailydown.py`

 -[采集文章效果](http://www.leon0204.com/weixin)
 - <a href="http://www.leon0204.com/weixinToday">采集热点，热点文章效果</a>

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


`TODO` :
1. dailyKeyword 采集热点关键词时，空数据时候插入，没数据是不会插入，没有写插入语句
2. 图片采集的优化 目前规则比较 


仅做学习用途
