# 02. 对评论进行分类2

[原文](http://blog.topspeedsnail.com/archives/10420)

## 数据

* [tweet 情绪数据集](http://help.sentiment140.com/for-students/)

数据集包含1百60万条推特，包含消极、中性和积极tweet。不知道有没有现成的微博数据集。

数据格式：移除表情符号的CSV文件，字段如下：

0. – the polarity of the tweet (0 = negative, 2 = neutral, 4 = positive)
1. – the id of the tweet (2087)
2. – the date of the tweet (Sat May 16 23:58:44 UTC 2009)
3. – the query (lyx). If there is no query, then this value is NO_QUERY.
4. – the user that tweeted (robotickilldozr)
5. – the text of the tweet (Lyx is cool)

training.1600000.processed.noemoticon.csv（238M）
testdata.manual.2009.06.14.csv（74K）

