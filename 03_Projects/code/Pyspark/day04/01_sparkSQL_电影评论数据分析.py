from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StringType,IntegerType,LongType
from pyspark.sql import functions as F

if __name__ == '__main__':
    spark = SparkSession.builder\
        .appName("movie")\
        .master("local[*]")\
        .getOrCreate()
    # 创建一个结构
    mv_schema = StructType()\
        .add("user_id", StringType(), nullable=False)\
        .add("movie_id", StringType(), nullable=False) \
        .add("rank", IntegerType(), nullable=False) \
        .add("ts", LongType(), nullable=False)
    # 读取CSV文件
    mv_df = spark.read.format("csv")\
        .option("header", False)\
        .option("sep", "\t")\
        .schema(mv_schema)\
        .load("file:///tmp/pycharm_project_652/day04/u.data")

    # 显示DF的内容 默认显示前20条
    mv_df.show()
    # 显示DF的结构
    mv_df.printSchema()
    # 显示数据量
    print(mv_df.count())

    # movielens 是一个整理好的数据集 可以跳过数据清洗和预处理

    # 创建视图
    mv_df.createTempView("movies")
    # 任务1：获取用户平均评分

    # 方法一 SQL语句
    u_df = spark.sql("select user_id,round(avg(rank),1) as avg_rank from movies group by user_id")
    u_df.show()

    # 方法二 DSL
    mv_df.groupBy("user_id").avg("rank")\
        .withColumnRenamed("avg(rank)", "avg_rank")\
        .withColumn("avg_rank", F.round("avg_rank",1))\
        .show()

    # 任务2：获取电影的平均分
    # 任务2.1 所有电影的平均分
    mv_all_avg_df = spark.sql("select round(avg(rank),1) from movies")
    mv_all_avg_df.show()
    # 任务2.2 每部电影的平均分
    mv_avg_df = spark.sql("select movie_id,round(avg(rank),1) from movies group by movie_id")
    mv_avg_df.show()

    # 任务3: 大于平均分电影的数量

    cnt = spark.sql("select movie_id,round(avg(rank),1) as avg_rank from movies group by movie_id having avg_rank>(select round(avg(rank),1) from movies)").count()
    print(cnt)

    # 任务4： 找到打高分（>3）次数最多的人 此人的平均分
    user_id = spark.sql("select user_id,count(rank) as cnt from movies where rank>3 group by user_id order by cnt desc").first()["user_id"]
    print(user_id)

    spark.sql("select round(avg(rank),1) from movies where user_id="+user_id).show()

    # 任务5： 每个用户的 最高分 最低分 平均分
    spark.sql("select user_id,max(rank),min(rank),round(avg(rank),1) as avg_rank from movies group by user_id").show()

    # DSL
    mv_df.groupBy("user_id").agg(
        F.round(F.avg("rank"),1),
        F.max("rank"),
        F.min("rank")
    ).show()

    # 任务6： 被评分次数超过100次的电影 的平均的TOP10

    spark.sql("select movie_id,count(rank) as cnt, round(avg(rank),1) as avg_rank from movies group by movie_id having cnt>100 order by avg_rank desc,cnt desc limit 10").show()