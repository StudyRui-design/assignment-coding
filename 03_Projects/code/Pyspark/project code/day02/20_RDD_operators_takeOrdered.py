# coding:utf8

from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 3, 2, 4, 7, 9, 6], 1)

    # 默认升序
    print(rdd.takeOrdered(3))

    # RDD 中按某种顺序排列的前 N 个元素
    # 这个简单的函数只是返回元素的负值，这意味着当 Spark 对元素进行排序时，
    # 它会认为较大的数字是较小的（因为它们的负值是较小的），从而得到降序排列的结果
    print(rdd.takeOrdered(3, lambda x: -x))
