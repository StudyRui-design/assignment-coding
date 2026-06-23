# coding=utf8
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

if __name__ == '__main__':
    spark = SparkSession.builder.master("local[*]").appName("spark_sql_test").getOrCreate()

    sc = spark.sparkContext

    # 读取单词到rdd中并按照空格来切分转换为[word]格式从而方便将rdd转换为DataFrame
    word_rdd = sc.textFile("file:///tmp/pycharm_001/data/words.txt").flatMap(lambda x: x.split(" ")).map(lambda x: [x])

    word_df = word_rdd.toDF(["word"])

    word_df.createTempView("words")

    spark.sql("select word,count(1) as cnt from words group by word order by  cnt desc ").show()

    #  API读取文本
    w_df = spark.read.format("text").load("file:///tmp/pycharm_001/data/words.txt")

    w_df.show()

    # withColumn 替换列
    # split 切割
    # explode 爆炸扩展行
    #df2 = w_df.withColumn("value", F.split(w_df["value"], " "))
    #df2.show()
    df2 = w_df.withColumn("value", F.explode(F.split(w_df["value"], " ")))
    # DSL风格
    df2=df2.groupby("value").count(). \
        withColumnRenamed("value", "word"). \
        withColumnRenamed("count", "cnt"). \
        orderBy("cnt", ascending=False)
    df2.show()