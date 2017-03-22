import tensorflow as tf
from utils import load_model


if __name__ == '__main__':
    path = './data/model.meta'
    with tf.Session() as sess:
        all_vars = load_model(sess, path)
