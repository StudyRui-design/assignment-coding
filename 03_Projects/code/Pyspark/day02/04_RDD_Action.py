from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")

    sc = SparkContext(conf=conf)

    rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6, 7])

    rdd2 = rdd1.map(lambda x: x+1)

    # collect 将所有的rdd分区数据收集到当前计算机内存中 返回一个本地集合
    # 小心使用 除非你可以确定返回元素的个数
    # print(rdd2.collect())

    # take 行动算子 获取指定个数的元素
    print(rdd2.take(2))
    # 返回元素的个数
    print(rdd2.count())
    # 降序并且取出指定个数
    print(rdd2.top(3))
    # 第一个元素
    print(rdd2.first())






