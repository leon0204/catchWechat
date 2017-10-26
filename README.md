# CatchWecaht
抓取微信公众号文章

pre：
   没有用框架，直接clone 就可以用 

 - `dailydown.py` ： <a href="http://www.leon0204.com/weixin" target="_blank">采集配置的公众号的文章效果</a>
 - `dailydownbyKeywords.py` ： <a target="_blank" href="http://www.leon0204.com/weixinToday">采集热点关键词，热门文章效果</a>   
 - `newcatch.py` ：  推荐使用，抓取指定 公众号url 

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


#### 优化
1 资源删除，热点抓取bug 修复

`TODO` :
1. ~~dailyKeyword 采集热点关键词时，空数据时候插入，没数据是不会插入，没有写插入语句~~
2. ~~图片采集的优化 ~~
3. 添加TDK 

#### 更新 v1
1. 优化图片采集规则，更全面抓取图片 
2. 修复一些bug 

如果对你有帮助的话，帮忙右上角star一下，谢谢！
欢迎 PR ～

