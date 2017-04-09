import os
import pickle

import tensorflow as tf
from nltk import word_tokenize

from learn_tensflow.blog_learn._01_comment_classification.train import lemmatizer


def main():
    train_filename = './data/train.csv'
    test_filename = './data/test.csv'
    lex_filename = './data/lex.pickle'

    with open(lex_filename, 'rb') as f:
        lex = pickle.load(f)

    train(train_filename, test_filename, lex)


def dataset_generator(file_name, lex, in_batch=True, bitch_size=100, buffer=1 << 15):
    """
    稀疏矩阵
    :param file_name: 文件名
    :param lex: 字典dict{单词: 单词索引(向量位置)}
    :param in_batch: 是否按批次获取
    :param bitch_size: 批次大小
    :param buffer: 缓冲大小
    :return: 稀疏矩阵值索引, 稀疏矩阵值, 稀疏矩阵形状, 对应的label矩阵
    """
    polarity_labels = {
        '0': [1, 0, 0],
        '2': [0, 1, 0],
        '4': [0, 0, 1],
    }
    with open(file_name, mode='r', buffering=buffer) as f:
        indexes, values, labels = [], [], []
        line_num = 0
        bitch_line_num = 0
        for line in f.readlines():
            index_values = {}
            polarity, tweet = line.split(',')
            label = polarity_labels[polarity]
            # 将句子拆分为单词
            words = word_tokenize(line.lower())
            for word in words:
                # 词形还原, 即如过去分词还原为动词原型
                word = lemmatizer.lemmatize(word)
                word_index = lex.get(word)
                if not word_index:
                    # 单词不在词典中
                    continue
                index_values[word_index] = index_values.get(word_index, 0) + 1
            for k, v in index_values.items():
                indexes.append((bitch_line_num, k))
                values.append(v)

            line_num += 1
            bitch_line_num += 1
            labels.append(label)

            if in_batch and bitch_line_num == bitch_size:
                # 达到批次数量, 输出
                shape = [bitch_line_num, len(lex)]
                yield indexes, values, shape, labels
                bitch_line_num = 0
                indexes, values, labels = [], [], []

        if in_batch and bitch_line_num != 0:
            shape = [bitch_line_num, len(lex)]
            yield indexes, values, shape, labels
        else:
            shape = [line_num, len(lex)]
            yield indexes, values, shape, labels
        return


def fnn_3L(X, Y, level_nums=None):
    """
    三层全链接模型
    :param X: 特征矩阵
    :param Y: 标签矩阵
    :param level_nums: 每一层的神经元数量
    :return: 输出与原标签
    """
    if level_nums is None:
        level_nums = [2000, 2000]
    input_shape = getattr(X, 'shape') or getattr(X, 'dense_shape')
    output_shape = Y.shape
    l1_fc = {'w_': tf.Variable(tf.random_normal([input_shape[1], level_nums[0]]), name='l1_fc_W_'),
             'b_': tf.Variable(tf.random_normal([level_nums[0]]), name='l1_fc_b_')}
    l2_fc = {'w_': tf.Variable(tf.random_normal([level_nums[0], level_nums[1]]), name='l2_fc_W_'),
             'b_': tf.Variable(tf.random_normal([level_nums[1]]), name='l2_fc_b_')}
    out_fc = {'w_': tf.Variable(tf.random_normal([level_nums[1], output_shape[1]]), name='out_fc_W_'),
              'b_': tf.Variable(tf.random_normal([output_shape[1]]), name='out_fc_b_')}

    l1_out = tf.nn.relu(tf.add(tf.matmul(X, l1_fc['w_']), l1_fc['b_']))
    l2_out = tf.nn.relu(tf.add(tf.matmul(l1_out, l2_fc['w_']), l2_fc['b_']))
    output = tf.add(tf.matmul(l2_out, out_fc['w_']), out_fc['b_'])

    return output, Y


def fnn_2L(X, Y, level_nums=None):
    """
    二层全链接模型
    :param X: 特征矩阵
    :param Y: 标签矩阵
    :param level_nums: 每一层的神经元数量
    :return: 输出与原标签
    """
    if level_nums is None:
        level_nums = [2000]
    input_shape = getattr(X, 'shape', None) or getattr(X, '_dense_shape')
    output_shape = Y.shape
    l1_fc = {'w_': tf.Variable(tf.random_normal([input_shape[1], level_nums[0]]), name='l1_fc_W_'),
             'b_': tf.Variable(tf.random_normal([level_nums[0]]), name='l1_fc_b_')}
    out_fc = {'w_': tf.Variable(tf.random_normal([level_nums[1], output_shape[1]]), name='out_fc_W_'),
              'b_': tf.Variable(tf.random_normal([output_shape[1]]), name='out_fc_b_')}

    l1_out = tf.nn.relu(tf.add(tf.matmul(X, l1_fc['w_']), l1_fc['b_']))
    output = tf.add(tf.matmul(l1_out, out_fc['w_']), out_fc['b_'])

    return output, Y


def train(train_filename, test_filename, lex):
    train_set_generator = dataset_generator(train_filename, lex, bitch_size=1000)
    test_indexes, test_values, test_shape, test_y = next(dataset_generator(test_filename, lex, in_batch=False))
    print(test_indexes[0], test_values[0], test_shape)
    test_x = tf.SparseTensor(indices=test_indexes, values=test_values, dense_shape=test_shape)
    X = tf.sparse_placeholder('float', shape=[None, len(lex)], name='X')
    Y = tf.placeholder('float', shape=[None, 3], name='Y')

    predict, y = fnn_2L(X, Y, level_nums=[2000])

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(predict, Y))
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    pre_accuracy = 0
    saver = tf.train.Saver()

    with tf.Session() as session:
        tf.initialize_all_variables()
        i = 0
        for indexes, values, shape, labels in train_set_generator:
            bitch_x = tf.SparseTensor(indexes, values, shape)
            bitch_y = labels
            session.run([cost, optimizer], feed_dict={X: bitch_x, Y: bitch_y})
            # 准确率
            if i > 50:
                correct = tf.equal(tf.argmax(predict, 1), tf.argmax(Y, 1))
                accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
                accuracy = accuracy.eval({X: test_x, Y: test_y})
                if accuracy > pre_accuracy:  # 保存准确率最高的训练模型
                    print('准确率: ', accuracy)
                    pre_accuracy = accuracy
                    saver.save(session, 'model.ckpt')  # 保存session
                i = 0
            i += 1


if __name__ == '__main__':
    os.chdir(os.path.split(__file__)[0] + '/..')
    main()
