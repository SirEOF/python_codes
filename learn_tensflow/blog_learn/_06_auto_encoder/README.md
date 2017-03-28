# 基于WiFi指纹的室内定位（autoencoder）

[原文](http://blog.topspeedsnail.com/archives/10468)

室内定位有很多种方式，利用WiFi指纹就是是其中的一种。在室内，可以通过WiFi信号强度来确定移动设备的大致位置，参看：https://www.zhihu.com/question/20593603。

# 步骤

首先采集WiFi信号，这并不需要什么专业的设备，几台手机即可。Android手机上有很多检测WiFi的App，如Sensor Log。

把室内划分成网格块(对应位置)，站在每个块内分别使用Sensor Log检测WiFi信号, 参考博客原文

下载数据
``` bash
$ wget https://archive.ics.uci.edu/ml/machine-learning-databases/00310/UJIndoorLoc.zip
$ unzip UJIndoorLoc.zip
```

