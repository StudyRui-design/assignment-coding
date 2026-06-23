from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 2, 3, 4, 5, 6, 7, 2, 3, 4, 5]

    data_rdd = sc.parallelize(data)

    rs_rdd = data_rdd.map(lambda x: x*10)

    # print(rs_rdd.count())
    # print(rs_rdd.take(5))
    # print(rs_rdd.first())
    print(rs_rdd.top(5))





