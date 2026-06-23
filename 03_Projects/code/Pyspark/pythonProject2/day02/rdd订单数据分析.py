from pyspark import SparkContext, SparkConf
import json
"""
需求：

读取order.text文件，提取北京的数据，组合北京和商品类别数据
同时对结果集进行去重, 得到北京售卖的商品类别信息
"""

if __name__ == '__main__':
    conf = SparkConf().setMaster("local[*]").setAppName("test")
    sc = SparkContext(conf=conf)

    file_rdd = sc.textFile("file:///tmp/pycharm_project_148/day02/order.text")
    # 数据之间用|分割 并且要降维
    order_rdd = file_rdd.flatMap(lambda x: x.split('|'))
    # json.loads 是一个python库函数 作用是将json字符串转换为python json字典类方便将来读取数据
    json_rdd = order_rdd.map(lambda str: json.loads(str))
    # 提取北京的数据
    bj_rdd = json_rdd.filter(lambda x: x['areaName'] == '北京')
    # 组合数据 并且去除重复的值
    rs_rdd = bj_rdd.map(lambda x: x['areaName']+"_"+x['category']).distinct()
    # 输出结果
    print(rs_rdd.collect())