from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")

    sc = SparkContext(conf=conf)

    rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6])

    # map rdd转换算子 运行的结果 是另外一个新RDD 允许使用链式编程 一直写多个RDD
    # 所有转换算子 默认是lazy
    rdd2 = rdd1.map(lambda a: a+1).map(lambda a: a+1)

    # rdd3 没有行动算子 没有被执行 lazy
    rdd3 = rdd2.map(lambda x: x/0)

    rdd4 = rdd2.map(lambda x: x+1)

    # 行动算子 相同于流水线的总开关 通常用来输出或者显示数据
    # 调用用完 行动算子后面不能直接继续使用转换算子
    # 每个RDD程序 至少有1个行动算子 使用行动算子 会执行所有和他有依赖关系算子
    # collect 的作用 是将所有的RDD数据集中起来 需要注意内容溢出问题
    print(rdd4.collect())

    li = rdd2.collect()
    print(type(li))



