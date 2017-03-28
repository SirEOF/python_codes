import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image


def weight_variable(shape, name=None):
    init = tf.truncated_normal(shape, stddev=0.1)
    var = tf.Variable(init, name=name)
    return var


def bias_variable(shape, name=None):
    init = tf.constant(0.1, shape=shape)
    var = tf.Variable(init, name=name)
    return var


def conv2d(x, w, strides=None, padding='VALID'):
    strides = strides or [1, 1, 1, 1]
    return tf.nn.conv2d(x, w, strides=strides, padding=padding)


def max_pool(x, shape=None, padding='VALID'):
    shape = [2, 2]
    return tf.nn.max_pool(x, ksize=[1, *shape, 1], strides=[1, *shape, 1], padding=padding)


def show_image(img, y=None):
    """ 显示图片
    :param img: 96 * 96 的灰度图像
    :param y: 0-1 的坐标点
    x, y = input_data(..)
    x1 = x[0]
    y1 = y[0]
    show_image(x1, y1)
    """
    if img.ndim in (1, 3):
        img = img.reshape(96, 96)
    plt.imshow(img)
    if y is not None:
        y = y.reshape((15, 2)) * 96
        y1, y2 = np.hsplit(y, 2)
        plt.scatter(y1, y2, c='red', s=3)
    plt.show()


def save_model(saver, sess, save_path):
    path = saver.save(sess, save_path)
    print('model save in: {0}'.format(path))


def load_model(sess, path):
    new_saver = tf.train.Saver()
    new_saver.restore(sess, path)


def load_other_img(path):
    img = Image.open(path)
    img = img.resize((96, 96))
    img = np.asarray(img)
    grey_img = np.mean(img, axis=2) / 255.
    return grey_img
