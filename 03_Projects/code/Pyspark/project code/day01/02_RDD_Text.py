from pyspark import SparkContext, SparkConf
if __name__ == '__main__':
    # 构建SparkContext对象
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    # 通过textFile API 读取数据

    # 读取本地文件数据
    file_rdd1 = sc.textFile("file:///tmp/pycharm_001/data/words.txt")
    print("默认读取分区数: ", file_rdd1.getNumPartitions())
    print("file_rdd1 内容:", file_rdd1.collect())

    # 加最小分区数参数的测试
    file_rdd2 = sc.textFile("file:///tmp/pycharm_001/data/words.txt", 3)
    # 最小分区数是参考值, Spark有自己的判断, 你给的太大Spark不会理会
    file_rdd3 = sc.textFile("file:///tmp/pycharm_001/data/words.txt", 100)
    print("file_rdd2 分区数:", file_rdd2.getNumPartitions())
    # spark有自己的分区策略 给的过大不会理会 通常是核心数量的整数倍 也和HDFS的块大小有一定的关系 过多的分区并不一定提高效率
    print("file_rdd3 分区数:", file_rdd3.getNumPartitions())

    print(file_rdd2)
    # 读取HDFS文件数据测试
    #hdfs_rdd = sc.textFile("hdfs://node1:8020/input/words.txt")
    #print("hdfs_rdd 内容:", hdfs_rdd.collect())