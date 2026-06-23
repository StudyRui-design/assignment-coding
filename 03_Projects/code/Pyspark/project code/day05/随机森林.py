from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorIndexer, VectorAssembler
from pyspark.sql.functions import col

if __name__ == '__main__':

    # 创建SparkSession
    spark = SparkSession.builder.appName("RandomForestIrisExample").getOrCreate()

    # 加载Iris数据集
    # Iris数据集通常包含四个特征（花萼长度、花萼宽度、花瓣长度、花瓣宽度）和一个标签（花的种类）
    # 这里我们假设数据集已经是一个DataFrame，并且特征列分别是'sepalLength', 'sepalWidth', 'petalLength', 'petalWidth'
    # 标签列是'species'
    data = spark.read.csv("iris.csv", header=True, inferSchema=True)

    data = data.withColumnRenamed("sepal length (cm)", "sepal_length")\
            .withColumnRenamed("sepal width (cm)", "sepal_width")\
            .withColumnRenamed("petal length (cm)", "petal_length")\
            .withColumnRenamed("petal width (cm)", "petal_width")
    data.show()


    vectorAssembler = VectorAssembler(inputCols=["sepal_length", "sepal_width", "petal_length", "petal_width"],
                                      outputCol="features")

    data_with_features = vectorAssembler.transform(data)

    data_with_features.show()

    # 划分数据集为训练集和测试集  
    (trainingData, testData) = data_with_features.randomSplit([0.7, 0.3])
    
    # 训练随机森林模型  
    rf = RandomForestClassifier(labelCol="species", featuresCol="features", numTrees=100, maxDepth=5)
    model = rf.fit(trainingData)
    
    # 做出预测  
    predictions = model.transform(testData)

    predictions.show()

    # 评估模型  
    evaluator = MulticlassClassificationEvaluator(
        labelCol="species", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test Error = %g " % (1.0 - accuracy))



    # 显示特征重要性  
    featureImportances = model.featureImportances
    print("Feature importances: %s" % featureImportances)
    
    # 停止SparkSession  
    spark.stop()
