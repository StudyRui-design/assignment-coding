import jieba


def context_jieba(data):

    jieba.load_userdict("my_dict")
    #jieba.del_word("的")
    r = jieba.cut(data)
    return r

def context_hotkey(data):
    # data[0] userid
    # data[1] searchKey
    words= context_jieba(data[1])
    returnlist = list()
    for word in words:
        returnlist.append((data[0]+"_"+word,1))
    return returnlist