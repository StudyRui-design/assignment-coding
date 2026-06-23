package edu.jxut.sft.config;

/**
 * Application configuration constants.
 * Centralized DB / Server / Spark settings.
 */
public final class AppConfig {

    private AppConfig() {}

    // ---- Server ----
    public static final int PORT = 9090;
    public static final String CONTEXT_PATH = "";

    // ---- Database ----
    public static final String DB_URL = "jdbc:mysql://127.0.0.1:3306/test"
            + "?useUnicode=true&characterEncoding=utf-8"
            + "&serverTimezone=Asia/Shanghai"
            + "&allowPublicKeyRetrieval=true"
            + "&useSSL=false";
    public static final String DB_USER = "root";
    public static final String DB_PASSWORD = "123456";

    // ---- Spark ----
    public static final String SPARK_APP_NAME = "SparkDataAnalysis";
    public static final String SPARK_MASTER = "local[*]";
    public static final String SPARK_DRIVER_MEMORY = "512m";
    public static final int SPARK_SHUFFLE_PARTITIONS = 2;
    public static final String SPARK_LOG_LEVEL = "WARN";

    // ---- API Prefixes ----
    public static final String API_STATS = "/api/stats";
    public static final String API_ML = "/api/ml";
    public static final String API_OPENAPI = "/api/openapi";
}
