from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")

    sc = SparkContext(conf=conf)

    rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6, 6])

    # filter 筛选 保留符合条件的元素
    # distinct 去除重复的元素
    # sortBy  按照执行的元素进行排序 ascending=False 降序 numPartitions=1 使用1个分区
    rdd2 = rdd1.filter(lambda x: x % 2 == 0)\
        .distinct()\
        .sortBy(lambda x: x, ascending=False, numPartitions=1)

    print(rdd2.collect())

    rdd3 = sc.parallelize([("南昌", 87), ("九江", 99), ("赣州", 95)])\
        .sortBy(lambda x: x[1],ascending=False, numPartitions=1)

    print(rdd3.collect())

    rdd4 = rdd3.filter(lambda x: x[0] == '九江').map(lambda x: x[1])

    print(rdd4.collect())

    
