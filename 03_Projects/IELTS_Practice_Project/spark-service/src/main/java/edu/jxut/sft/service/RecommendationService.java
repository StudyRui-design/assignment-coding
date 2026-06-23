package edu.jxut.sft.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import edu.jxut.sft.dao.SubjectDao;
import edu.jxut.sft.dao.UserDao;
import edu.jxut.sft.exception.ApiException;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.util.HashSet;
import java.util.Set;

/**
 * Business logic for ML / recommendation APIs.
 */
public class RecommendationService {

    private final SubjectDao subjectDao = new SubjectDao();
    private final UserDao userDao = new UserDao();

    /**
     * KMeans-style user behavior clustering (simplified via rating profile).
     */
    public JSONArray userClusters() {
        try {
            JSONArray arr = new JSONArray();
            Dataset<Row> df = subjectDao.allSubjects();
            // Aggregate user-subject rating matrix into clusters
            Dataset<Row> clusterDf = subjectDao.readFromMySQL(
                    "SELECT " +
                    "  CASE WHEN ac.avgRating >= 4.0 THEN '高活跃' " +
                    "       WHEN ac.avgRating >= 3.0 THEN '中等活跃' " +
                    "       ELSE '低活跃' END AS cluster, " +
                    "  COUNT(DISTINCT ac.user_id) AS userCount, " +
                    "  ROUND(AVG(ac.avgRating), 2) AS avgRating " +
                    "FROM (SELECT user_id, AVG(rating) AS avgRating " +
                    "      FROM user_subject_rating GROUP BY user_id) ac " +
                    "GROUP BY cluster ORDER BY avgRating DESC");
            for (Row row : clusterDf.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("cluster", row.getString(0));
                item.put("userCount", row.getLong(1));
                item.put("avgRating", row.isNullAt(2) ? 0 : ((Number) row.get(2)).doubleValue());
                arr.add(item);
            }
            return arr;
        } catch (Exception e) {
            throw new ApiException("Failed to run cluster analysis", e);
        }
    }

    /**
     * Default hot subject recommendations.
     */
    public JSONArray defaultRecommendations() {
        try {
            JSONArray arr = new JSONArray();
            Dataset<Row> df = subjectDao.hotSubjects();
            int rank = 1;
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                double avg = row.isNullAt(3) ? 0 : ((Number) row.get(3)).doubleValue();
                long learners = row.getLong(2);
                item.put("score", avg);
                item.put("reason", "热门好评 · " + avg + "分 · " + learners + "人学习");
                item.put("rank", rank++);
                arr.add(item);
            }
            return arr;
        } catch (Exception e) {
            throw new ApiException("Failed to load recommendations", e);
        }
    }

    /**
     * Personalized recommendations for a given user.
     */
    public JSONArray personalizedRecommendations(int userId) {
        try {
            // Get user's learned subject IDs
            Set<Integer> learnedIds = new HashSet<>();
            Dataset<Row> userDf = userDao.allUsers();
            String username = null;
            for (Row r : userDf.collectAsList()) {
                if (r.getInt(0) == userId) {
                    username = r.getString(1);
                    break;
                }
            }
            if (username != null) {
                learnedIds = userDao.getLearnedSubjectIds(username);
            }

            String excludeClause = "";
            if (!learnedIds.isEmpty()) {
                StringBuilder sb = new StringBuilder(" AND r.subject_id NOT IN (");
                boolean first = true;
                for (int id : learnedIds) {
                    if (!first) sb.append(",");
                    sb.append(id);
                    first = false;
                }
                sb.append(")");
                excludeClause = sb.toString();
            }

            Dataset<Row> df = subjectDao.unlearnedHighRatedSubjects(excludeClause);
            JSONArray arr = new JSONArray();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                double score = row.isNullAt(2) ? 0 : ((Number) row.get(2)).doubleValue();
                long raters = row.getLong(3);
                item.put("score", score);
                item.put("reason", "根据你的兴趣推荐 · " + score + "分 · " + raters + "人评价");
                arr.add(item);
            }

            // Fill up to 5 with defaults
            if (arr.size() < 5) {
                JSONArray defaults = defaultRecommendations();
                Set<String> existing = new HashSet<>();
                for (int i = 0; i < arr.size(); i++) {
                    existing.add(arr.getJSONObject(i).getString("name"));
                }
                for (int i = 0; i < defaults.size() && arr.size() < 5; i++) {
                    if (!existing.contains(defaults.getJSONObject(i).getString("name"))) {
                        arr.add(defaults.getJSONObject(i));
                    }
                }
            }
            return arr;
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException("Failed to generate personalized recommendations", e);
        }
    }
}
