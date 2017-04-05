import random
from collections import Counter

import numpy as np
import tensorflow as tf
from nltk import word_tokenize, WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


def main():
    pos_file = './data/pos.txt'
    neg_file = './data/neg.txt'
    lex = create_lexicon(pos_file=pos_file, neg_file=neg_file)
    data_set = standardize_dataset(pos_file, neg_file, lex)
    train(data_set)


def train(dataset, epochs=100, batch_size=50):
    """
    训练
    :param dataset: 数据集[[features, label], ...]
    :param epochs: 迭代次数
    :param batch_size: 批次大小
    :return:
    """
    # 拆分测试集合
    total = len(dataset)
    test_count = int(0.1 * total)
    test_data = dataset[:test_count]
    train_data = dataset[test_count:]
    input_num = len(train_data[0][0])

    X = tf.placeholder('float', [None, input_num], name='X')
    Y = tf.placeholder('float', name='Y')
    predict, labels = nn_model(X, Y, 2)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=predict, labels=labels))
    optimizer = tf.train.AdamOptimizer().minimize(cost)

    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        for epoch in range(epochs):
            epoch_loss = 0
            random.shuffle(train_data)
            i = 0
            X_input = train_data[0, :]
            Y_input = train_data[1, :]
            while i < len(train_data):
                start = i
                i += batch_size
                end = i
                _, c = session.run([optimizer, cost], feed_dict={X: X_input[start:end], Y: Y_input[start:end]})
                epoch_loss += c

            print('epoch: %s \t epoch_loss: %s' % (epoch, epoch_loss))

        X_input = test_data[0, :]
        Y_input = test_data[1, :]
        correct = tf.equal(tf.argmax(predict, 1), tf.argmax(Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('准确率: ', accuracy.eval({X: X_input, Y: Y_input}))
        print('correct: ', correct.eval({X: X_input, Y: Y_input}))


def nn_model(data, labels, out_num, l1_neural_num=1000):
    """
    神经网络模型
        这里使用两层主要是:
        第一层(隐藏层)体现词与词之间体现的特征
        第二层(输出层)体现这些特征对于正负态度之间的贡献度
    :param list, np.array data: 输入数据
    :param int out_num: 输出数量
    :param int l1_neural_num: 第一层的神经元数量
    :return:
    """
    input_shape = data.shape
    l1_fc = {
        'W': tf.Variable(tf.random_normal([input_shape[1].value, l1_neural_num]), name='l1_fc_W'),
        'b': tf.Variable(tf.random_normal([l1_neural_num]), name='l1_fc_b'),
    }

    out_fc = {
        'W': tf.Variable(tf.random_normal([l1_neural_num, out_num]), name='l2_fc_W'),
        'b': tf.Variable(tf.random_normal([out_num]), name='l2_fc_b'),
    }

    l1_fc_out = tf.add(tf.matmul(data, l1_fc['W']), l1_fc['b'], name='l1_fc_out')
    l1_relu_out = tf.nn.relu(l1_fc_out, name='l1_relu_out')

    out_fc_out = tf.add(tf.matmul(l1_relu_out, out_fc['W']), out_fc['b'], name='out_fc_out')
    return out_fc_out, labels


def standardize_dataset(pos_file, neg_file, lex, save=''):
    """
    对数据进行标准化
    :param pos_file: 正面评论文件名
    :param neg_file: 负面评论文件名
    :param dict lex: 字典
    :param str save: 不为空则保存至指定路径
    :return list: 输入矩阵
    """
    dataset = []
    with open(pos_file, 'r') as f:
        lines = f.readlines()
        for review in lines:
            pos_vector = string2vector(lex, review)
            dataset.append([pos_vector, [1, 0]])
    with open(neg_file, 'r') as f:
        lines = f.readlines()
        for review in lines:
            neg_vector = string2vector(lex, review)
            dataset.append(neg_vector)
            dataset.append([neg_vector, [0, 1]])
    return np.array(dataset)


def string2vector(lex, review):
    """
    评论转向量
    :param dict lex: 可用用的单词字典{word: position}
    :param str review: 评论
    :return np.array: 评论对应的向量
    """
    # 句子拆分为单词
    words = word_tokenize(review.lower())
    # 词形还原, 即如过去分词还原为动词原型
    words = map(lemmatizer.lemmatize, words)

    features = np.zeros([len(lex)])
    for word in words:
        pos = lex.get(word)
        if pos is None:
            continue
        features[pos] += 1
    return features


def create_lexicon(pos_file, neg_file):
    """
    创建词汇表
    :param str pos_file: 正面评论文件名
    :param str neg_file: 负面评论文件名
    :return dict: 可用用的单词字典{word: position}
    """
    pos_words = process_file(pos_file)
    neg_words = process_file(neg_file)
    lex = pos_words + neg_words
    total_count = len(lex)

    word_count = Counter(lex)

    # 只取出现频率在百分之十到百分之五十的单词
    low_limit = total_count * 0.1
    high_limit = total_count * 0.5

    lex = [w for w, c in word_count.items() if low_limit < c < high_limit]
    return {word: pos for pos, word in enumerate(lex)}


def process_file(file_name):
    """
    将文件拆分为单词
    :param file_name: 文件名
    :return:单词列表
    """
    lex = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            # 将句子拆分为单词
            words = word_tokenize(line.lower())
            for word in words:
                # 词形还原, 即如过去分词还原为动词原型
                lex.append(lemmatizer.lemmatize(word))
    return lex


if __name__ == '__main__':
    main()
