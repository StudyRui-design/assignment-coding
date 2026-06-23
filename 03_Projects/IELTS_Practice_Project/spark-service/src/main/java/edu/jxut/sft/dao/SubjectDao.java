package edu.jxut.sft.dao;

import com.alibaba.fastjson.JSONArray;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 * DAO for subject-related Spark SQL queries.
 */
public class SubjectDao extends BaseDao {

    /** Subject overview: total count + status distribution */
    public Dataset<Row> subjectOverview() {
        return readFromMySQL(
                "SELECT COUNT(*) AS total, " +
                "SUM(CASE WHEN status='启用' THEN 1 ELSE 0 END) AS enabled, " +
                "SUM(CASE WHEN status='禁用' THEN 1 ELSE 0 END) AS disabled " +
                "FROM subject");
    }

    /** Subject status group-by */
    public Dataset<Row> subjectStatusDistribution() {
        return readFromMySQL(
                "SELECT status, COUNT(*) AS cnt FROM subject GROUP BY status");
    }

    /** All subjects (simple list) */
    public Dataset<Row> allSubjects() {
        return readFromMySQL("SELECT id, name, status, creator FROM subject");
    }

    /** Subject learning distribution / popularity */
    public Dataset<Row> subjectStudyDistribution() {
        return readFromMySQL(
                "SELECT s.name, COUNT(st.id) AS studyCount, " +
                "COUNT(DISTINCT st.creator) AS learnerCount " +
                "FROM subject s LEFT JOIN study st ON s.id = st.subject_id " +
                "GROUP BY s.name ORDER BY studyCount DESC");
    }

    /** Subject ranking by average rating */
    public Dataset<Row> subjectRanking() {
        return readFromMySQL(
                "SELECT r.subject_id, s.name, " +
                "COUNT(DISTINCT r.user_id) AS learnerCount, " +
                "ROUND(AVG(r.rating), 1) AS avgRating, " +
                "COUNT(r.rating) AS ratingCount " +
                "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                "GROUP BY r.subject_id, s.name " +
                "ORDER BY avgRating DESC, learnerCount DESC");
    }

    /** Hot subjects (avg rating >= 4.0) */
    public Dataset<Row> hotSubjects() {
        return readFromMySQL(
                "SELECT r.subject_id, s.name, " +
                "COUNT(DISTINCT r.user_id) AS learnerCount, " +
                "ROUND(AVG(r.rating), 1) AS avgRating " +
                "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                "GROUP BY r.subject_id, s.name " +
                "HAVING AVG(r.rating) >= 4.0 " +
                "ORDER BY avgRating DESC, learnerCount DESC");
    }

    /** Subjects NOT learned by a given user (for personalized recommendation) */
    public Dataset<Row> unlearnedHighRatedSubjects(String excludeCondition) {
        String sql = "SELECT r.subject_id, s.name, " +
                "ROUND(AVG(r.rating), 1) AS avgScore, " +
                "COUNT(r.user_id) AS raterCount " +
                "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                "WHERE r.rating >= 4.0" + excludeCondition +
                " GROUP BY r.subject_id, s.name " +
                "ORDER BY avgScore DESC, raterCount DESC LIMIT 5";
        return readFromMySQL(sql);
    }
}
