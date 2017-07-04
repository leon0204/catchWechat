# CatchWecaht
抓取微信公众号文章

pre：
	没有用框架，直接clone 就可以用。

####  获取代码
```
	cd /home/wwwroot
	git clone https://github.com/leon0204/catchWecaht.git
```

#### 导入模板数据库，先创建weixin 数据库 utf8mb4
```	
	cd catchWecaht
	mysql -uroot -p weixin < ./weixin.sql
```

>抓取公众号的列表在weixin 数据库的 subscription表中 


配置所需要用到的库，没有的用pip基本都可以满足



#### 抓取公众号今日更新列表
```
	// 需要设置一下 dailydown.py 中的数据库设置
	python dailydown.py
```
数据会存在 subcatch 表中 
