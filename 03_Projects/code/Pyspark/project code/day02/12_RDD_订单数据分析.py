from pyspark import SparkContext, SparkConf
import json
import os

#  yarn 在client模式下运行 使用OS模块可设置系统环境变量
os.environ['HADOOP_CONF_DIR'] = "/software/hadoop-3.2.0/etc/hadoop"

if __name__ == '__main__':
    # 设置运行模式和APP名称
    # conf = SparkConf().setMaster("yarn").setAppName("test-yarn-1")
    conf = SparkConf().setMaster("local[*]").setAppName("test-local-order")
    # 设置配置文件
    sc = SparkContext(conf=conf)

    # 本地模式路径
    f_rdd = sc.textFile("file:///tmp/pycharm_001/data/order.text")
    #f_rdd = sc.textFile("../data/order.text")
    # HDFS路径 注意文件的权限问题
    #f_rdd = sc.textFile("hdfs://hadoop102:8020/input/order.text")

    # flatMap算子切分元素
    jsons_rdd = f_rdd.flatMap(lambda line: line.split("|"))

    # 使用python json库的loads方法将json字符串转换为字典类型
    dic_rdd = jsons_rdd.map(lambda json_str: json.loads(json_str))

    # 使用filter算子过滤
    bj_rdd = dic_rdd.filter(lambda s:s['areaName'] == '北京')

    # map算子迭代所有元素拼接结果
    rs_rdd = bj_rdd.map(lambda x: x['areaName'] + "_" +x['category']).distinct()

    # 打印结果
    print(rs_rdd.collect())