import jieba

if __name__ == '__main__':
    str = "大数据学院学习大数据技术"
    jieba.load_userdict('my_dict')
    r = jieba.cut(str)
    print(list(r))