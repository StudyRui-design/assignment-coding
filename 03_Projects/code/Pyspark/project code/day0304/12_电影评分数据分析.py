# coding:utf8

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType
import pandas as pd
from pyspark.sql import functions as F

if __name__ == '__main__':
    spark = SparkSession.builder.appName("spl_test_movie").\
        master("local[*]").\
        config("spark.sql.shuffle.partitions", 2).\
        getOrCreate()

    """
       spark.sql.shuffle.partitions 参数指的是, 在sql计算中, shuffle算子阶段默认的分区数是200个.
       对于集群模式来说, 200个默认也算比较合适
       如果在local下运行, 200个很多, 在调度上会带来额外的损耗
       所以在local下建议修改比较低 比如2\4\10均可
       这个参数和Spark RDD中设置并行度的参数 是相互独立的.
    """


    # 1. 读取数据集
    # 创建df结构
    # user_id 用户id movie_id 电影id rank评分等级 ts评论时间
    mv_schema = StructType().add("user_id", StringType(), nullable=True). \
        add("movie_id", IntegerType(), nullable=True). \
        add("rank", IntegerType(), nullable=True). \
        add("ts", StringType(), nullable=True)
    # 读取csv文件填充df
    mv_df = spark.read.format("csv"). \
        option("sep", "\t"). \
        option("header", False). \
        option("encoding", "utf-8"). \
        schema(schema=mv_schema). \
        load("../data/u.data")
    mv_df.show()
    # 任务1：用户平均分

    mv_df.createTempView("movies")

    spark.sql("select user_id,round(avg(rank),1) as avg_rank from movies group by user_id order by avg_rank desc ").show()

    # 任务2：每部电影的平均分

    # spark.sql("select movie_id,round(avg(rank),1) as avg_rank from movies group by movie_id").show()
    # DSL风格
    mv_df.groupby("movie_id").avg("rank").\
        withColumnRenamed("avg(rank)", "avg_rank").\
        withColumn("avg_rank", F.round("avg_rank", 1)).\
        orderBy("avg_rank", ascending=False)

    # 任务3: 查询大于平均分的电影
    spark.sql("select movie_id,rank from movies where rank>(select avg(rank) from movies) order by rank").show()
    # DSl风格查询大于平均分的电影数量
    print("大于平均分电影的数量: ", mv_df.where(mv_df['rank'] > mv_df.select(F.avg(mv_df['rank'])).first()['avg(rank)']).count())

    # 任务4：查询高分电影中(>3)打分次数最多的用户, 此人打分的平均分
    userid = spark.sql("select user_id,count(1) as cnt from movies where rank>3 group by user_id order by cnt desc limit 1").first()["user_id"]
    spark.sql("select avg(rank) from movies where user_id="+userid).show()

    '''
    # DSL 风格
    user_id = mv_df.where("rank > 3").\
        groupBy("user_id").\
        count().\
        withColumnRenamed("count", "cnt").\
        orderBy("cnt", ascending=False).\
        limit(1).\
        first()['user_id']
      # 求平均分  
      df.filter(df['user_id'] == user_id).\
        select(F.round(F.avg("rank"), 2)).show()   
    '''
    # 任务5 查询每个用户的平均分,最高分,最低分
    spark.sql("select user_id,avg(rank),max(rank),min(rank) from movies group by user_id").show()

    '''DSL风格
    # agg方法可以添加多个聚合
    mv_df.groupBy("user_id"). \
        agg(
        F.round(F.avg("rank"), 2).alias("avg_rank"),
        F.min("rank").alias("min_rank"),
        F.max("rank").alias("max_rank")
    ).show()
    '''

    # 任务6 查询评分超过100次的电影的平均分排名top10
    spark.sql("select movie_id,avg_rank from (select movie_id,round(avg(rank),2) as avg_rank,\
        count(*) as cnt from movies group by movie_id) \
        where cnt>100 order by avg_rank desc limit 10").show()

    '''DSL风格 获取的结果一致 
    mv_df.groupBy("movie_id"). \
        agg(
        F.count("movie_id").alias("cnt"),
        F.round(F.avg("rank"), 2).alias("avg_rank")
    ).where("cnt > 100"). \
        orderBy("avg_rank", ascending=False). \
        limit(10). \
        show()
    '''
"""
1. agg: 它是GroupedData对象的API, 作用是 在里面可以写多个聚合
2. alias: 它是Column对象的API, 可以针对一个列 进行改名
3. withColumnRenamed: 它是DataFrame的API, 可以对DF中的列进行改名, 一次改一个列, 改多个列 可以链式调用
4. orderBy: DataFrame的API, 进行排序, 参数1是被排序的列, 参数2是 升序(True) 或 降序 False
5. first: DataFrame的API, 取出DF的第一行数据, 返回值结果是Row对象.
# Row对象 就是一个数组, 你可以通过row['列名'] 来取出当前行中, 某一列的具体数值. 返回值不再是DF 或者GroupedData 或者Column而是具体的值(字符串, 数字等)
"""