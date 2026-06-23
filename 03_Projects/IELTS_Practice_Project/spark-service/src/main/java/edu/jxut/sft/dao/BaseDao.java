package edu.jxut.sft.dao;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import edu.jxut.sft.config.AppConfig;
import edu.jxut.sft.config.SparkConfig;
import edu.jxut.sft.exception.ApiException;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.util.Properties;

/**
 * Base DAO providing shared Spark SQL / JDBC helpers.
 */
public class BaseDao {

    protected SparkSession spark;

    public BaseDao() {
        this.spark = SparkConfig.getSparkSession();
    }

    /**
     * Read from MySQL via Spark JDBC datasource.
     */
    public Dataset<Row> readFromMySQL(String customSql) {
        try {
            Properties props = new Properties();
            props.setProperty("user", AppConfig.DB_USER);
            props.setProperty("password", AppConfig.DB_PASSWORD);
            props.setProperty("useSSL", "false");
            props.setProperty("allowPublicKeyRetrieval", "true");
            props.setProperty("serverTimezone", "Asia/Shanghai");

            if (customSql != null && !customSql.trim().isEmpty()) {
                return spark.read().jdbc(AppConfig.DB_URL,
                        "(" + customSql + ") AS tmp", props);
            }
            throw new ApiException("SQL must not be empty");
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Database query failed: " + e.getMessage(), e);
        }
    }

    /**
     * Execute a DDL / DML via raw JDBC (for setup / teardown).
     */
    protected void executeJDBC(String sql) {
        try (Connection conn = DriverManager.getConnection(
                AppConfig.DB_URL, AppConfig.DB_USER, AppConfig.DB_PASSWORD);
             Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        } catch (Exception e) {
            throw new ApiException("JDBC execute failed: " + e.getMessage(), e);
        }
    }

    /**
     * Convert a Spark Dataset to a FastJSON JSONArray.
     */
    protected JSONArray rowsToArray(Dataset<Row> df) {
        JSONArray arr = new JSONArray();
        for (Row row : df.collectAsList()) {
            JSONObject obj = new JSONObject(true);
            String[] fieldNames = df.columns();
            for (int i = 0; i < fieldNames.length; i++) {
                if (!row.isNullAt(i)) {
                    Object val = row.get(i);
                    if (val instanceof Number) {
                        obj.put(fieldNames[i], ((Number) val).doubleValue());
                    } else {
                        obj.put(fieldNames[i], val.toString());
                    }
                } else {
                    obj.put(fieldNames[i], null);
                }
            }
            arr.add(obj);
        }
        return arr;
    }
}
