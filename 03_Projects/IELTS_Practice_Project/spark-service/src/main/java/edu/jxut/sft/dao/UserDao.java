package edu.jxut.sft.dao;

import com.alibaba.fastjson.JSONArray;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.util.HashSet;
import java.util.Set;

/**
 * DAO for user-related Spark SQL queries.
 */
public class UserDao extends BaseDao {

    /** Total user count + type distribution */
    public Dataset<Row> userOverview() {
        return readFromMySQL(
                "SELECT COUNT(*) AS total, user_type FROM user GROUP BY user_type");
    }

    /** User type breakdown */
    public Dataset<Row> userTypeDistribution() {
        return readFromMySQL(
                "SELECT user_type, COUNT(*) AS cnt FROM user GROUP BY user_type");
    }

    /** Top N users by study time */
    public Dataset<Row> topStudyUsers(int limit) {
        return readFromMySQL(
                "SELECT u.username, u.real_name, u.user_type, " +
                "COALESCE(SUM(st.study_duration), 0) AS totalDuration, " +
                "COUNT(st.id) AS studyCount " +
                "FROM user u LEFT JOIN study st ON u.username = st.creator " +
                "GROUP BY u.username, u.real_name, u.user_type " +
                "ORDER BY totalDuration DESC LIMIT " + limit);
    }

    /** Get subject IDs learned by a specific user */
    public Set<Integer> getLearnedSubjectIds(String username) {
        Set<Integer> ids = new HashSet<>();
        // 输入校验：用户名只允许字母/数字/下划线/中文，防止SQL注入
        if (username == null || !username.matches("^[a-zA-Z0-9_\\-\\u4e00-\\u9fa5]+$")) {
            return ids;
        }
        try {
            Dataset<Row> df = readFromMySQL(
                    "SELECT DISTINCT subject_id FROM study WHERE creator='" +
                    username.replace("'", "''") + "'");
            for (Row r : df.collectAsList()) {
                if (!r.isNullAt(0)) ids.add(r.getInt(0));
            }
        } catch (Exception e) {
            // no learned records
        }
        return ids;
    }

    /** All users list (limited) */
    public Dataset<Row> allUsers() {
        return readFromMySQL(
                "SELECT id, username, real_name, user_type FROM user ORDER BY id");
    }
}
