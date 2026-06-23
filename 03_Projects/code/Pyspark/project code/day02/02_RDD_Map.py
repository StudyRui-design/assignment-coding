from pyspark import SparkConf, SparkContext

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")

    sc = SparkContext(conf=conf)

    rdd1 = sc.parallelize([1, 2, 3, 4, 5, 6])

    # map算子 将RDD中的元素 一个一个拿出来执行 （）里面的函数
    # lambda的本质是一个匿名函数
    rdd2 = rdd1.map(lambda x: x+1)

    def add1(x):
        return x+1
    # 如果使用 实名自定义函数(方法) 不能写括号 只能写名字
    # 当将要执行的业务逻辑很简单通常就直接写lambda 复杂的场景使用实名函数
    rdd3 = rdd1.map(add1)

    print(rdd2.collect())
    print(rdd3.collect())

    
