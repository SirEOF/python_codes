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

## 在原作者基础上的修改

我认为网络两层足够了, 3层容易出现过拟合的问题, 这两层分别表示

        第一层(隐藏层)体现词与词之间体现的特征
        第二层(输出层)体现这些特征对于正负态度之间的贡献度

正确率从作者的 `66%` 提升至 `85%`

```
epoch: 0 	 epoch_loss: 1927.28561748
epoch: 1 	 epoch_loss: 504.113170767
epoch: 2 	 epoch_loss: 49.8831254835
epoch: 3 	 epoch_loss: 2.40500953082
epoch: 4 	 epoch_loss: 0.00867240004624
epoch: 5 	 epoch_loss: 0.00161984394917
epoch: 6 	 epoch_loss: 0.00016255728438
epoch: 7 	 epoch_loss: 0.000153592895653
epoch: 8 	 epoch_loss: 0.000146943874405
epoch: 9 	 epoch_loss: 2.86102199709e-08
准确率:  0.850844
```
