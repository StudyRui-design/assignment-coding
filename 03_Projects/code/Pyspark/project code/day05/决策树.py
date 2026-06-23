# coding=utf8
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Spark mllib 决策树
if __name__ == '__main__':
    print("machine learning in spark")
    spark = SparkSession.builder.appName("test-spark-mllib").getOrCreate()

    data = spark.read.csv("iris.csv", header=True, inferSchema=True)

    data = data.withColumnRenamed("sepal length (cm)", "sepal_length")\
        .withColumnRenamed("sepal width (cm)", "sepal_width")\
        .withColumnRenamed("petal length (cm)", "petal_length")\
        .withColumnRenamed("petal width (cm)", "petal_width")
    data.show()

    # 将特征列组合成一个特征向量
    assembler = VectorAssembler(inputCols=["sepal_length", "sepal_width", "petal_length", "petal_width"],
                                outputCol="features")
    output = assembler.transform(data)

    # 选择特征和标签列
    final_data = output.select("features", "species")

    # 划分训练集和测试集
    (trainingData, testData) = final_data.randomSplit([0.7, 0.3])

    # 创建决策树分类器
    dt = DecisionTreeClassifier(labelCol="species", featuresCol="features")

    # 训练模型
    model = dt.fit(trainingData)

    # 进行预测
    predictions = model.transform(testData)


    predictions.show()

    # 评估模型
    evaluator = MulticlassClassificationEvaluator(
        labelCol="species", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)


    print("准确率：", round(accuracy*100, 1), "%")
    # 停止SparkSession
    spark.stop()
