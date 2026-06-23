import jieba

def context_jieba(data):
    jieba.load_userdict('my_dict')
    r = jieba.cut(data)
    return  r

def context_user(data):
    words = context_jieba(data[1])
    li = list()
    for word in words:
        li.append((data[0]+"_"+word, 1))
    return li

