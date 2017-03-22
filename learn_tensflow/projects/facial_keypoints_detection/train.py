
import random

from utils import *
from input import *

def model(x, y, keep_prob):
    filter1 = weight_variable([3, 3, 1, 32])
    bias1 = bias_variable([32])

    h_conv1 = tf.nn.relu(conv2d(x, filter1) + bias1)
    h_pool1 = max_pool(h_conv1, (2,2))

    filter2 = weight_variable([2, 2, 32, 64])
    bias2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, filter2) + bias2)
    h_pool2 = max_pool(h_conv2, (2, 2))

    filter3 = weight_variable([2, 2, 64, 128])
    bias3 = bias_variable([128])

    h_conv3 = tf.nn.relu(conv2d(h_pool2, filter3) + bias3)
    h_pool3 = max_pool(h_conv3, (2, 2))

    w_fc1 = weight_variable([11 * 11 * 128, 500])
    b_fc1 = bias_variable([500])

    h_pool3_flat = tf.reshape(h_pool3, [-1, 11 * 11 * 128])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool3_flat, w_fc1) + b_fc1)

    w_fc2 = weight_variable([500, 500])
    b_fc2 = bias_variable([500])

    h_fc2 = tf.nn.relu(tf.matmul(h_fc1, w_fc2) + b_fc2)
    h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)

    w_fc3 = weight_variable([500, 30])
    b_fc3 = bias_variable([30])

    y_conv = tf.matmul(h_fc2_drop, w_fc3) + b_fc3
    rmse = tf.sqrt(tf.reduce_mean(tf.square(y - y_conv)))
    return y_conv, rmse

VALIDATION_SIZE = 100  # 验证集大小
EPOCHS = 100  # 迭代次数
BATCH_SIZE = 64  # 每个batch大小
EARLY_STOP_PATIENCE = 10  # 控制early stopping的参数

if __name__ == '__main__':
    sess = tf.InteractiveSession()
    x = tf.placeholder(tf.float32, shape=[None, 96, 96, 1], name='x')
    y_ = tf.placeholder(tf.float32, shape=[None, 30], name='y_')
    keep_prob = tf.placeholder(tf.float32)

    y_conv, rmse = model(x, y_, keep_prob)
    train_step = tf.train.AdamOptimizer(1e-3).minimize(rmse)

    sess.run(tf.initialize_all_variables())

    X, y = input_data(TRAIN_FILE)

    X_valid, y_valid = X[:VALIDATION_SIZE], y[:VALIDATION_SIZE]
    X_train, y_train = X[VALIDATION_SIZE:], y[VALIDATION_SIZE:]

    best_validation_loss = 1000000.
    current_epoch = 0

    TRAIN_SIZE = X_train.shape[0]
    train_index = list(range(TRAIN_SIZE))
    random.shuffle(train_index)

    X_train, y_train = X_train[train_index], y_train[train_index]

    saver = tf.train.Saver()

    print('begin training..., train data set size:{0}'.format(TRAIN_SIZE))
    for i in range(EPOCHS):
        random.shuffle(train_index)  # 每个epoch都shuffle一下效果更好
        X_train, y_train = X_train[train_index], y_train[train_index]

        for j in range(0, TRAIN_SIZE, BATCH_SIZE):
            print('epoch {0}, train {1} samples done...'.format(i, j))
            train_step.run(feed_dict={
                x: X_train[j: j + BATCH_SIZE],
                y_: y_train[j: j + BATCH_SIZE],
                keep_prob: 0.5,
            })

        validation_loss = rmse.eval(feed_dict={x: X_train, y_: y_train, keep_prob: 1.0})
        print('epoch {0} done! validation loss:{1}'.format(i, validation_loss * 96.0))
        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            current_epoch = i
            save_model(saver, sess, SAVE_PATH)  # 即时保存最好的结果
        elif (i - current_epoch) >= EARLY_STOP_PATIENCE:
            print('early stopping')
            break