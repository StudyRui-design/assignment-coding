# coding=utf8

from pyspark import SparkContext, SparkConf
from defs import context_jieba,context_hotkey
from pyspark.storagelevel import StorageLevel

if __name__ == '__main__':
    # 设置运行模式和APP名称
    conf = SparkConf().setMaster("local[*]").setAppName("test-local-1")
    # 设置配置文件
    sc = SparkContext(conf=conf)
    # 读取数据文件
    #rs_rdd = sc.textFile("file:///tmp/pycharm_001/data/Sogou.txt")
    rs_rdd = sc.textFile("../data/Sogou.txt")
    # 切分数据
    sp_rs_rdd = rs_rdd.map(lambda x: x.split("\t"))

    # 多次使用的rdd可启用缓存 缓存在磁盘上
    sp_rs_rdd.persist(storageLevel=StorageLevel.DISK_ONLY)


    """任务1：获取搜索关键字的前五"""
    # 取出数据的第3列
    ss_rdd = sp_rs_rdd.map(lambda x: x[2])
    # 调用jieba进行分词处理
    jieba_rs = ss_rdd.flatMap(context_jieba)
    # 转换为统计元组
    rs = jieba_rs.map(lambda a: (a, 1))

    # 聚合并排序 取前五take(5)
    # sortBy  ascending=False 降序 全局排序所以使用一个分区numPartitions=1
    final_result = rs.reduceByKey(lambda a, b: a+b).sortBy(lambda x: x[1], ascending=False, numPartitions=1).take(5)
    print("关键字前5：")
    print(final_result)

    """任务2：用户和关键字组合分析 获取用户热词"""
    user_content_rdd = sp_rs_rdd.map(lambda x: (x[1], x[2]))

    user_hotkey_rdd = user_content_rdd.flatMap(context_hotkey)

    rs_hotkey = user_hotkey_rdd.reduceByKey(lambda a, b: a+b).sortBy(lambda x: x[1], ascending=False, numPartitions=1).take(5)

    print("用户热词：")
    print(rs_hotkey)

    """任务3：热门搜索时间段分析"""

    time_rdd = sp_rs_rdd.map(lambda x: (x[0].split(":")[0], 1))

    rs_time_rdd= time_rdd.reduceByKey(lambda a, b: a+b).sortBy(lambda x: x[1], ascending=False, numPartitions=1)

    print("热们搜索时间段")
    print(rs_time_rdd.collect())
