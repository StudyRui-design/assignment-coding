from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 2, 3, 4, 5, 6, 7, 2, 3, 4, 5]

    data_rdd = sc.parallelize(data)
    # 去重
    rs_rdd = data_rdd.distinct()

    print(rs_rdd.collect())

    # 排序  ascending=False 降序
    # 分区1 numPartitions=1
    r_rdd = rs_rdd.sortBy(lambda x: x, ascending=False, numPartitions=1)

    print(r_rdd.collect())