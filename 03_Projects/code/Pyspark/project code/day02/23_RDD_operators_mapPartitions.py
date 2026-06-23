# coding:utf8

from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 3, 2, 4, 7, 9, 6], 3)

    def process(iter):
        result = list()
        for it in iter:
            result.append(it * 10)

        return result

    # 和foreach不同 mapPartitions算子返回的是RDD 而且操作的目标是分区 在分布式计算中效率高
    print(rdd.mapPartitions(process).collect())