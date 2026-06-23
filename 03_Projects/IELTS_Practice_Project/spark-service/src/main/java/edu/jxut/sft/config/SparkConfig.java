package edu.jxut.sft.config;

import org.apache.spark.sql.SparkSession;

/**
 * Initializes and manages the shared SparkSession singleton.
 */
public class SparkConfig {

    private static SparkSession spark;

    /**
     * Get or create the singleton SparkSession.
     */
    public static synchronized SparkSession getSparkSession() {
        if (spark == null) {
            spark = SparkSession.builder()
                    .appName(AppConfig.SPARK_APP_NAME)
                    .master(AppConfig.SPARK_MASTER)
                    .config("spark.driver.memory", AppConfig.SPARK_DRIVER_MEMORY)
                    .config("spark.sql.shuffle.partitions", AppConfig.SPARK_SHUFFLE_PARTITIONS)
                    .getOrCreate();
            spark.sparkContext().setLogLevel(AppConfig.SPARK_LOG_LEVEL);
            System.out.println("✓ SparkSession initialized (v" + spark.version() + ")");
        }
        return spark;
    }

    /**
     * Gracefully stop the SparkSession.
     */
    public static synchronized void close() {
        if (spark != null) {
            spark.stop();
            spark = null;
            System.out.println("✓ SparkSession stopped");
        }
    }
}
