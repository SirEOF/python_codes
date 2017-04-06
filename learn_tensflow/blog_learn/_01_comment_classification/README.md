# 01. 对评论进行分类1

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


# 总结

在整理数据的时候, 总是需要把features和labels放在同一个数组里边, 因为后续需要进行shuffle.
第二是array的shuffle不能使用random包里边的shuffle, 而是需要使用numpy.random包里边的shuffle
第三是feed的数据不能是array, 必须是list
