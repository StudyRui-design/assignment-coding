from pyspark import SparkConf, SparkContext
from defs import context_jieba,context_user

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    # 读取文件
    s_rdd = sc.textFile("file:///tmp/pycharm_project_48/day03/Sogou.txt")

    # 切割数据
    sp_rdd = s_rdd.map(lambda x: x.split("\t"))

    print(sp_rdd.take(20))


    # 任务1 统计热搜词 被搜索次数最多的词
    # 找出第3列 用户输入的内容 内容可能是一句话 需要使用jieba分词 调用自定义函数context_jieba
    w_rdd = sp_rdd.map(lambda x: x[2]).flatMap(context_jieba)
    # 分词之后 统计并且排序
    hot_word_rdd = w_rdd.map(lambda x: (x, 1))\
        .reduceByKey(lambda a, b: a+b)\
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)

    print(hot_word_rdd.take(20))

    # 任务2 用户搜索统计 统计 用户_词 的次数
    # 找到用户ID 和 用户输入的内容
    u_w_rdd = sp_rdd.map(lambda x: (x[1],x[2]))

    user_hot_rdd = u_w_rdd.flatMap(context_user) \
        .reduceByKey(lambda a, b: a + b) \
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)

    print(user_hot_rdd.take(10))

    # 任务3 热搜时间段 统计 哪个时间使用的人数最多
    # 获取时间字段中 小时
    h_rdd = sp_rdd.map(lambda x:x[0].split(":")[0])
    # 统计并且排序
    hot_time_rdd = h_rdd.map(lambda x: (x, 1)) \
        .reduceByKey(lambda a, b: a + b) \
        .sortBy(lambda x: x[1], ascending=False, numPartitions=1)
    print(hot_time_rdd.collect())