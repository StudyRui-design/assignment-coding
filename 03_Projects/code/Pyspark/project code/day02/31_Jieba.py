import jieba

if __name__ == '__main__':
    jieba.load_userdict("my_dict")
    jieba.del_word("我")
    jieba.del_word("想")

    r = jieba.cut("我想去江西科技学院人工智能学院")

    print(list(r))