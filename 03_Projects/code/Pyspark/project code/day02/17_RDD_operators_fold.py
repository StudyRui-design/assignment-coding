# coding:utf8

from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 2, 3, 4, 5], 3)

    # 分区进行折叠
    # 1+2+3+4+5 =15  分区数 3+1=4 4*10=40 40+15=55
    # 初始值*(节点数目+1) + Rdd各元素求和
    print(rdd.fold(10, lambda a, b: a + b))

    rdd2 = sc.parallelize([1, 2, 3, 4, 5], 3)

    print(rdd2.glom().collect())
    # [[1], [2, 3], [4, 5]]
    # 11  15  19  先按分区进行累加
    # 10 +(11+15+19) 再次折叠聚合
    print(rdd2.fold(10, lambda a, b: a + b))

    rdd3 = sc.parallelize([1, 2, 3, 4, 5], 1)
    # 10+1+2+3+4+5
    # 10+(10+1+2+3+4+5)
    print(rdd3.fold(10, lambda a, b: a + b))

    # 分布式环境下使用fold算子需要注意性能问题
