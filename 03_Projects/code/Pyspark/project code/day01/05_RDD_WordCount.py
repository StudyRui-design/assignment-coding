from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setAppName("test-app").setMaster("local[*]")

    sc = SparkContext(conf=conf)
    # 读取文件
    wordRDD = sc.textFile("file:///tmp/pycharm_001/data/words.txt")

    flatMapRDD = wordRDD.flatMap(lambda line: line.split(" "))

    # 将格式转换为 (x,1)
    mapRDD = flatMapRDD.map(lambda x: (x, 1))

    # 按key进行组合
    resultRDD = mapRDD.reduceByKey(lambda a, b: a + b)

    rs_rdd_col2 = resultRDD.collect()

    print(resultRDD.getNumPartitions())

    for line in rs_rdd_col2:
        print(line)

    # 写入目录 可以是文件系统 也可以是HDFS路径
    #resultRDD.saveAsTextFile("file:///tmp/pycharm_001/data/result")

    sc.stop()