import operator
import os
import pickle
import random

from nltk import word_tokenize, WordNetLemmatizer

os.chdir(os.path.split(__file__)[0] + '/..')
lemmatizer = WordNetLemmatizer()


def main():
    """
    清理输入
    """
    data_filename = './data/training.1600000.processed.noemoticon.csv'
    test_filename = './data/testdata.manual.2009.06.14.csv'
    # 创建字典文件
    lex = get_lexicon(data_filename)
    with open('./data/lex.pickle', mode='wb') as lex_file:
        pickle.dump(lex, lex_file)
    extra_columns(data_filename, './data/train.csv')
    extra_columns(test_filename, './data/test.csv')


def get_lexicon(file_name):
    """
    创建词汇表
    :param str pos_file: 正面评论文件名
    :param str neg_file: 负面评论文件名
    :return dict: 可用用的单词字典{word: position}
    """
    word_count = file_to_word_counter(file_name)

    low_limit = 0.94  # 大部分没吊用
    high_limit = 0.9991

    words = [_[0] for _ in sorted(word_count.items(), key=operator.itemgetter(1))]
    total_count = len(word_count)
    lex = words[int(low_limit * total_count): int(high_limit * total_count)]
    del words
    return {word: pos for pos, word in enumerate(lex)}


def file_to_word_counter(file_name):
    """
    将文件拆分为单词
    :param file_name: 文件名
    :return:单词列表
    """
    lex = {}
    with open(file_name, mode='r', encoding='latin-1', buffering=1 << 15) as f:
        for line in f.readlines():
            # 将句子拆分为单词
            words = word_tokenize(line.lower())
            for word in words:
                # 词形还原, 即如过去分词还原为动词原型
                word = lemmatizer.lemmatize(word)
                lex[word] = lex.get(word, 0) + 1
    return lex


def extra_columns(file_name, out_name):
    """ 把文件中仅存的两列抽取出来
    """
    with open(file_name, mode='r', encoding='latin-1', buffering=1 << 15) as f, open(out_name, mode='w', buffering=1 << 10) as t:
        new_lines = []
        lines = f.readlines()
        for line in lines:
            line = line.replace('"', '').split(',')
            polarity = line[0]
            tweet = line[-1]
            new_lines.append(polarity + ',' + tweet)
        random.shuffle(new_lines)
        t.writelines(new_lines)

if __name__ == '__main__':
    main()
