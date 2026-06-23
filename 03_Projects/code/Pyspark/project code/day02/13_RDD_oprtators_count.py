# coding:utf8

from pyspark import SparkConf, SparkContext


if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 2, 3, 4, 5], 3)

    # 获取数量
    print(rdd.count())