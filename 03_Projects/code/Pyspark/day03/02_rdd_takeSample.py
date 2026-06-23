from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setAppName("test").setMaster("local[*]")
    sc = SparkContext(conf=conf)

    rdd = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9])

    # 行动算子 随机获取指定数量的数据
    # False 不能选中重复位置 和里面的数据无关
    # num 获取元素的数量
    # 随机数种子 穿入相同的种子 可以保证结果能够复现
    print(rdd.takeSample(False, 5, 10))
