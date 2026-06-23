# coding=utf8

from pyspark import SparkContext, SparkConf
from pyspark.storagelevel import StorageLevel

if __name__ == '__main__':
    conf = SparkConf().setAppName("test-homework").setMaster("local[*]")
    sc = SparkContext(conf=conf)
    log_rdd = sc.textFile("../data/apache.log")
    sp_log_rdd = log_rdd.map(lambda x: x.split(" "))

    sp_log_rdd.persist(StorageLevel.DISK_ONLY)

    '''获取每个用户访问次数及访问用户总数'''
    ip_rdd = sp_log_rdd.map(lambda x: (x[0], 1))
    ip_v_rdd = ip_rdd.reduceByKey(lambda a, b: a+b)
    print(ip_v_rdd.collect())
    ip_count = len(ip_v_rdd.collect());

    '''获取访问量前五的HTML页面'''
    page_rdd = sp_log_rdd.filter(lambda x:x[6].find(".html")!=-1).map(lambda x: (x[6], 1))
    page_v_rdd = page_rdd.reduceByKey(lambda a, b: a+b).sortBy(lambda x: x[1], ascending=False, numPartitions=1)
    result = page_v_rdd.take(5)
    print(result)