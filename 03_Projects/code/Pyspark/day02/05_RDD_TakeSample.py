from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")

    sc = SparkContext(conf=conf)

    rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])

    # 随机选取
    # True 允许重复位置 False不允许重复位置
    # 5 取5个元素
    # 随机数种子 当指定了种子 每次都可以得到相同的内容
    print(rdd1.takeSample(False, 5, 999))