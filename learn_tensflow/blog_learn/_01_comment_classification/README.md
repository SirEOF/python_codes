# 01. 对评论进行分类

[原文](http://blog.topspeedsnail.com/archives/10399)

## 数据

* neg.txt：5331条负面电影评论 [下载](http://blog.topspeedsnail.com/wp-content/uploads/2016/11/neg.txt)
* pos.txt：5331条正面电影评论 [下载](http://blog.topspeedsnail.com/wp-content/uploads/2016/11/pos.txt)

## 步骤

* 安装nltk库

``` bash
pip install nltk
```

* 下载nltk库的数据

``` python
import nltk
nltk.download()
```

* 训练, 见代码`train.py`

## 结果

准确率真tm喜人，才60%多，比瞎猜强点有限。

那么问题出在哪呢？

准确率低主要是因为数据量太小，同样的模型，如果使用超大数据训练，准确率会有显著的提升。
