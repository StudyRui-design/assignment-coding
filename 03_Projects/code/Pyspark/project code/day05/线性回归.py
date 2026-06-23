from pyspark.ml.evaluation import MulticlassClassificationEvaluator, RegressionEvaluator
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.ml.linalg import Vectors
from pyspark.ml.regression import LinearRegression
from pyspark.sql import functions as F
from pyspark.sql import SparkSession


if __name__ == '__main__':
    spark = SparkSession.builder.appName("LinearRegression").getOrCreate()
    data = spark.read.csv("boston_house.csv", header=True, inferSchema=True)

    vectorAssembler = VectorAssembler(inputCols=["CRIM","ZN","INDUS","CHAS","NOX","RM","AGE","DIS","RAD","TAX","PTRATIO","B","LSTAT"],
                                      outputCol="features")
    df_with_features = vectorAssembler.transform(data)

    df_with_features.show()

    # 划分数据集为训练集和测试集
    (trainingData, testData) = df_with_features.randomSplit([0.7, 0.3])

    # 创建线性回归模型
    lr = LinearRegression(featuresCol="features", labelCol="MEDV")

    # 训练模型
    lrModel = lr.fit(trainingData)

    print(lrModel.coefficients)

    # 对测试集进行预测
    predictions = lrModel.transform(testData)

    print(lrModel.coefficients)

    predictions.show()

    # 计算均方误差（Mean Squared Error）
    evaluator = RegressionEvaluator(labelCol="MEDV", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    print("Root Mean Squared Error (RMSE) on test data = " + str(rmse))

    print("均方误差（Mean Squared Error）：", rmse)


    spark.stop()




