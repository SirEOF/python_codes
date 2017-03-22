import tensorflow as tf

def weight(shape, name=None):
    init = tf.truncated_normal(shape, stddev=0.1)
    var = tf.Variable(init, name=name)
    return var

def bias(shape, name=None):
    init = tf.constant(0.1, shape=shape)
    var = tf.Variable(init, name=name)
    return var

def conv2d(x, w, strides=None, padding='VALID'):
    strides = strides or [1, 1, 1, 1]
    return tf.nn.conv2d(x, w, strides=strides, padding=padding)

def max_pool(x, shape=None, padding='VALID'):
    shape = [2, 2]
    return tf.nn.max_pool(x, ksize=[1, *shape, 1], strides=[1, *shape, 1], padding=padding)
