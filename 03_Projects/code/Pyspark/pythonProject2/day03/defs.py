import jieba


def context_jieba(str):
    jieba.load_userdict('my_dict')
    r = jieba.cut(str)
    return r


def context_user_word(data):
    # data[0]  用户id
    # data[1]  输入的内容
    # 调用上面的函数对输入内容进行分词
    words = context_jieba(data[1])
    ul = list()
    # 组合用户ID和分词
    for word in words:
        ul.append(data[0] + "_" + word)
    return ul
