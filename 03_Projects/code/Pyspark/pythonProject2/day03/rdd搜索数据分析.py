from pyspark import SparkContext, SparkConf
from pyspark.storagelevel import StorageLevel
import json
from defs import context_jieba, context_user_word
"""
需求：
1.热搜词
2.用户词
3.热搜时间段
"""

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    file_rdd = sc.textFile('file:///tmp/pycharm_project_148/day03/Sogou.txt')

    sogou_rdd = file_rdd.map(lambda x: x.split("\t"))

    # 通过观察sogou_rdd 会被多次调用 可以使用缓存技术
    sogou_rdd.persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
    # 任务1 获取热搜词排行
    # 1.1找到用户的输入
    ss_rdd = sogou_rdd.map(lambda x: x[2])
    # 1.2分词 将输入的内容变成词条
    # context_jieba 自定义的函数 来自defs 功能是将一句话 转换为词组
    words_rdd = ss_rdd.flatMap(context_jieba)
    # 1.3统计词条出现的次数并排序
    rs_word_rdd = words_rdd.map(lambda word: (word, 1))\
        .reduceByKey(lambda a, b: a+b)\
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)
    print(rs_word_rdd.take(10))
    # 任务2 用户词
    # 2.1 找出用户 和 搜索内容
    user_ss_rdd = sogou_rdd.map(lambda x: (x[1], x[2]))
    # 2.2 搜索内容转换为词条 组合用户和词条
    user_words_rdd = user_ss_rdd.flatMap(context_user_word)
    # 2.3 统计用户搜索词条的次数 并且排序
    rs_user_words_rdd = user_words_rdd.map(lambda word: (word, 1))\
        .reduceByKey(lambda a, b: a+b)\
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)
    print(rs_user_words_rdd.take(10))

    # 任务 3.热搜时间段
    # 3.1 找到时间 取出小时
    time_rdd = sogou_rdd.map(lambda x: x[0].split(":")[0])
    # 3.2 分组统计和排序
    rs_time_rdd = time_rdd.map(lambda h: (h, 1))\
        .reduceByKey(lambda a, b: a+b)\
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)
    print(rs_time_rdd.collect())