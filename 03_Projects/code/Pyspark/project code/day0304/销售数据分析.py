# coding=utf8

from pyspark.sql import SparkSession
from pyspark.storagelevel import StorageLevel
from pyspark.sql import functions as F

if __name__ == '__main__':
    spark = SparkSession.builder. \
        appName("test"). \
        master("local[*]"). \
        config("spark.sql.shuffle.partitions", 16).\
        config("spark.driver.extraClassPath",\
               "/software/anaconda3/envs/pyspark/lib/python3.8/site-packages/pyspark/jars/mysql-connector-java-5.1.41-bin.jar")\
        .getOrCreate()

    # 1. 读取数据
    # 省份信息, 缺失值过滤, 同时省份信息中 会有"null" 字符串
    # 订单的金额, 数据集中有的订单的金额是单笔超过10000的, 这些是测试数据
    # 手动列值裁剪(虽然SparkSQL会自动做这个优化)
    # "storeProvince",所在省
    # "storeID",商店ID
    # "receivable",收款金额
    # "dateTS", 订单日期
    # "payType" 支付类型
    # ../data/mini.json
    df = spark.read.format("json").load("file:///tmp/pycharm_001/data/mini.json"). \
        dropna(thresh=1, subset=['storeProvince']). \
        filter("storeProvince != 'null'"). \
        filter("receivable < 10000"). \
        select("storeProvince", "storeID", "receivable", "dateTS", "payType")

    df.createTempView("storeView")
    # 任务1：各省销售额统计
    province_sale_df = spark.sql("select storeProvince,sum(receivable) as sum_receivable from storeView\
                    group by storeProvince order by sum_receivable desc")

    province_sale_df.show()
    # 写入mysql
    province_sale_df.write.mode("overwrite"). \
        format("jdbc"). \
        option("url", "jdbc:mysql://192.168.220.1/bigdata?useUnicode=true&characterEncoding=utf8"). \
        option("dbtable", "province_sale"). \
        option("user", "root"). \
        option("password", "123"). \
        save()

    # 任务2：TOP3销售省份中, 有哪些店铺达到过日销售额1000+

    top3_gt1000_df = spark.sql("select storeID,sum(receivable) as sum_receivable ,to_date(from_unixtime(dateTS/1000)) as d_dataTS from storeView \
                    where  storeProvince in \
                    (select storeProvince from storeView \
                        group by storeProvince \
                        order by sum(receivable) desc limit 3) \
                    group by storeID,d_dataTS").filter("sum_receivable>1000")
    top3_gt1000_df.show()
    # 写入mysql
    province_sale_df.write.mode("overwrite"). \
        format("jdbc"). \
        option("url", "jdbc:mysql://192.168.220.1:3306/bigdata?useUnicode=true&characterEncoding=utf8"). \
        option("dbtable", "top3_gt1000"). \
        option("user", "root"). \
        option("password", "123"). \
        save()

    '''DSL风格
    # 2.1 先找到TOP3的销售省份
    top3_province_df = province_sale_df.limit(3).select("storeProvince").withColumnRenamed("storeProvince",
                                                                                           "top3_province")

    # 2.2 和 原始的DF进行内关联, 数据关联后, 就是全部都是TOP3省份的销售数据了
    top3_province_df_joined = df.join(top3_province_df, on=df['storeProvince'] == top3_province_df['top3_province'])

    top3_province_df_joined.persist(StorageLevel.MEMORY_AND_DISK)
    # 广东省 1 2021-01-03    1005  

    # from_unixtime的精度是秒级, 数据的精度是毫秒级, 要对数据进行精度的裁剪
    province_hot_store_df = top3_province_df_joined.groupBy("storeProvince", "storeID",
                                                                  F.from_unixtime(df['dateTS'].substr(0, 10),
                                                                                  "yyyy-MM-dd").alias("day")). \
        sum("receivable").withColumnRenamed("sum(receivable)", "money"). \
        filter("money > 1000")

    province_hot_store_df.show()
    '''

    # TOP3 省份中 各个省份的平均订单价格(单单价)
    top3_avg_receivable_df = spark.sql("select storeProvince,avg(receivable) as avg_receivable from storeView as t \
                        where storeProvince in \
                        (select storeProvince from storeView \
                        group by storeProvince \
                        order by sum(receivable) desc limit 3) \
                        group by storeProvince")
    top3_avg_receivable_df.show()

    top3_avg_receivable_df.write.mode("overwrite"). \
        format("jdbc"). \
        option("url", "jdbc:mysql://192.168.220.1:3306/bigdata?useUnicode=true&characterEncoding=utf8"). \
        option("dbtable", "top3_avg_receivable"). \
        option("user", "root"). \
        option("password", "123"). \
        save()

    # 需求4: TOP3 省份中, 各个省份的支付比例
    top_pay_df = spark.sql(" select detail_view.storeProvince,detail_view.payType,concat(round((detail_view.type_total/total_view.pay_total)*100,2),'%') as percent  from (select storeProvince, payType, count(1) as type_total from storeView \
                            group by payType,storeProvince) as detail_view left join (select storeProvince, count(payType) as pay_total from storeView group by storeProvince) as total_view on detail_view.storeProvince=total_view.storeProvince")
    top_pay_df.show()
    top_pay_df.write.mode("overwrite"). \
        format("jdbc"). \
        option("url", "jdbc:mysql://192.168.220.1:3306/bigdata?useUnicode=true&characterEncoding=utf8"). \
        option("dbtable", "top_pay"). \
        option("user", "root"). \
        option("password", "123"). \
        save()