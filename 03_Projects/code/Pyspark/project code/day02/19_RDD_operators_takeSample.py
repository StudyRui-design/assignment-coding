# coding:utf8

from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 3, 5, 3, 1, 3, 2, 6, 7, 8, 6], 1)

    # 参数1 表示是否会取同一个位置的数据 注意是位置 不是数值
    # 参数2 抽取个数
    # 参数3 随机数种子 如果不给spark随机给  给了会使得每次的结果一样
    print(rdd.takeSample(False, 5, 1))
