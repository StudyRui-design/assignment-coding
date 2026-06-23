from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 2, 3, 4, 5, 6, 7, 2, 3, 4, 5]

    data_rdd = sc.parallelize(data)

    # filter 过滤 保留符合条件的元素
    rs_rdd = data_rdd.filter(lambda x: x % 2 == 0)

    # 注意 行动算子不会生成新的RDD
    # 通常行动算子放在代码的最后面
    print(rs_rdd.collect())