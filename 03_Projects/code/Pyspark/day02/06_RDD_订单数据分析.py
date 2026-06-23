from pyspark import SparkConf, SparkContext
import json

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("hello")
    sc = SparkContext(conf=conf)
    # 读取order.text文件，提取北京的数据，组合北京和商品类别数据
    # 同时对结果集进行去重, 得到北京售卖的商品类别信息
    #读取文件 得到初始RDD
    order_rdd = sc.textFile("file:///tmp/pycharm_project_42/day02/order.text")

    # 切割数据 并且降维 得到JSON格式的集合
    json_rdd = order_rdd.flatMap(lambda x: x.split('|'))

    # 将JSON转为DICT类型方便操作
    # json.laods
    dict_rdd = json_rdd.map(lambda x: json.loads(x))
    # filter 筛选出北京的数据
    # map 重组元素 北京_类别
    # distinct 去重重复
    bj_rdd = dict_rdd.filter(lambda x: x['areaName'] == '北京')\
        .map(lambda x: x['areaName']+'_'+x['category']).distinct()

    print(bj_rdd.collect())
