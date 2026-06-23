from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 2, 3, 4, 5, 6, 7, 2, 3, 4, 5]

    data_rdd = sc.parallelize(data)
    # 去重
    rs_rdd = data_rdd.distinct()

    print(rs_rdd.collect())