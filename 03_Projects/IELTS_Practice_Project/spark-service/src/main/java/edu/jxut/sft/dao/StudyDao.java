package edu.jxut.sft.dao;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 * DAO for study-record and rating related Spark SQL queries.
 */
public class StudyDao extends BaseDao {

    /** Overall study count */
    public Dataset<Row> studyCount() {
        return readFromMySQL("SELECT COUNT(*) AS cnt FROM study");
    }

    /** Overall rating count */
    public Dataset<Row> ratingCount() {
        return readFromMySQL("SELECT COUNT(*) AS cnt FROM user_subject_rating");
    }

    /** Rating statistics grouped by score */
    public Dataset<Row> ratingDistribution() {
        return readFromMySQL(
                "SELECT rating, COUNT(*) AS cnt FROM user_subject_rating " +
                "GROUP BY rating ORDER BY rating");
    }

    /** Study records per day (for trend analysis) */
    public Dataset<Row> studyTrend() {
        return readFromMySQL(
                "SELECT DATE(create_time) AS day, COUNT(*) AS cnt " +
                "FROM study WHERE create_time IS NOT NULL " +
                "GROUP BY DATE(create_time) ORDER BY day");
    }

    /** Study duration stats */
    public Dataset<Row> studyDurationStats() {
        return readFromMySQL(
                "SELECT " +
                "COALESCE(SUM(study_duration), 0) AS totalDuration, " +
                "COALESCE(AVG(study_duration), 0) AS avgDuration, " +
                "COUNT(*) AS totalRecords " +
                "FROM study");
    }
}
