import jieba

if __name__ == '__main__':
    words ='在江西科技学院学习大数据技术'
    jieba.load_userdict('my_dict')
    r = jieba.cut(words)

    print(list(r))