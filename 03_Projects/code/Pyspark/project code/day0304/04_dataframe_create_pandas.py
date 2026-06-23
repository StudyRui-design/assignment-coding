# coding:utf8

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType
import pandas as pd


if __name__ == '__main__':
    # 0. 构建执行环境入口对象SparkSession
    spark = SparkSession.builder.\
        appName("test").\
        master("local[*]").\
        getOrCreate()
    sc = spark.sparkContext

    data = {'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'Salary': [50000, 60000, 70000]}
    df_pandas = pd.DataFrame(data)
    print(df_pandas)

    # 注意：部分版本的pyspark 此方法有BUG 会调用错误的属性 升级新版本后正常
    df = spark.createDataFrame(df_pandas)

    df.show()


    # df = spark.createDataFrame(pdf)
    #
    # df.printSchema()
    # df.show()
