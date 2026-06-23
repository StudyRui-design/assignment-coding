from pyspark import SparkContext, SparkConf

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    data = [1, 1, 1, 1, 5, 6, 7]

    data_rdd = sc.parallelize(data)

    # 第一个参数 False 不能获取相同位置的数据
    # 第二参数 取出元素的个数
    # 第三参数 随机数种子 指定相同种子 得到相同的随机结果
    print(data_rdd.takeSample(False, 6, 1))
