from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 2, 3, 4, 5, 6, 7, 2, 3, 4, 5]

    data_rdd = sc.parallelize(data)

    # map 将元素一个一个取出来 执行函数
    # 转换算子 将一个转换为另外一个RDD 这2个RDD存在依赖关系
    rs_rdd = data_rdd.map(lambda x: x+10)
    r2_rdd = rs_rdd.map(lambda x: x+1)
    # collect 行动算子 会将所有的分区中的数据拉取到同一个集合中
    # 在真实开发中 要小心使用 否则很容易造成客户端程序内存溢出
    # 只有在有行动算子的情况下 相关的RDD代码才会执行
    print(r2_rdd.collect())


