from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 2, 3, 4, 5, 6])

    rdd1 = rdd.map(lambda x: x+1)

    # 行动算子
    # collect 拉取所有的数据到同一个服务器并且返回本地 list集合
    # 实际开发中 要小心使用 容易造成内存撑爆了
    # print(rdd1.collect())

    # count 返回元素的个数
    # 注意：行动算子 可以有多个 返回不再是RDD
    # print(rdd1.count())

    # 行动算子 获取指定条数的数据
    print(rdd1.take(3))

    print(rdd1.top(3))

    print(rdd1.first())