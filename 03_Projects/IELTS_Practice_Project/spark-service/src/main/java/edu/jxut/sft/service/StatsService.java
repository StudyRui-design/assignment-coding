package edu.jxut.sft.service;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import edu.jxut.sft.dao.StudyDao;
import edu.jxut.sft.dao.SubjectDao;
import edu.jxut.sft.dao.UserDao;
import edu.jxut.sft.exception.ApiException;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 * Business logic for statistics APIs.
 */
public class StatsService {

    private final SubjectDao subjectDao = new SubjectDao();
    private final UserDao userDao = new UserDao();
    private final StudyDao studyDao = new StudyDao();

    /**
     * System overview: aggregate counts.
     */
    public JSONObject overview() {
        JSONObject result = new JSONObject(true);

        // User count
        long userCount = 0;
        JSONObject userType = new JSONObject(true);
        try {
            Dataset<Row> uDf = userDao.userTypeDistribution();
            for (Row r : uDf.collectAsList()) {
                String type = r.getString(0);
                long cnt = r.getLong(1);
                userCount += cnt;
                userType.put(type, cnt);
            }
        } catch (Exception e) {
            throw new ApiException("Failed to load user stats", e);
        }
        result.put("userCount", userCount);
        result.put("userType", userType);

        // Subject count
        long subjectCount = 0, enabledCount = 0, disabledCount = 0;
        JSONObject subjectStatus = new JSONObject(true);
        try {
            Dataset<Row> sDf = subjectDao.subjectStatusDistribution();
            for (Row r : sDf.collectAsList()) {
                String status = r.getString(0);
                long cnt = r.getLong(1);
                subjectCount += cnt;
                subjectStatus.put(status, cnt);
                if ("启用".equals(status)) enabledCount = cnt;
                if ("禁用".equals(status)) disabledCount = cnt;
            }
        } catch (Exception e) {
            throw new ApiException("Failed to load subject stats", e);
        }
        result.put("subjectCount", subjectCount);
        result.put("subjectStatus", subjectStatus);
        result.put("availableCount", enabledCount);
        result.put("disabledCount", disabledCount);

        // Study & rating count
        try {
            Dataset<Row> stDf = studyDao.studyCount();
            if (stDf.count() > 0) result.put("studyCount", stDf.first().getLong(0));
            Dataset<Row> rDf = studyDao.ratingCount();
            if (rDf.count() > 0) result.put("ratingCount", rDf.first().getLong(0));
        } catch (Exception e) {
            throw new ApiException("Failed to load study stats", e);
        }

        return result;
    }

    /**
     * Subject study distribution.
     */
    public JSONArray subjectDistribution() {
        try {
            JSONArray arr = new JSONArray();
            Dataset<Row> df = subjectDao.subjectStudyDistribution();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("name", row.getString(0));
                item.put("studyCount", row.isNullAt(1) ? 0 : row.getLong(1));
                item.put("learnerCount", row.isNullAt(2) ? 0 : row.getLong(2));
                arr.add(item);
            }
            return arr;
        } catch (Exception e) {
            throw new ApiException("Failed to load subject distribution", e);
        }
    }

    /**
     * Top study users.
     */
    public JSONArray topUsers(int limit) {
        if (limit <= 0) limit = 10;
        try {
            JSONArray arr = new JSONArray();
            Dataset<Row> df = userDao.topStudyUsers(limit);
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("username", row.getString(0));
                item.put("realName", row.isNullAt(1) ? "" : row.getString(1));
                item.put("userType", row.isNullAt(2) ? "" : row.getString(2));
                item.put("totalDuration", row.isNullAt(3) ? 0 : row.getLong(3));
                item.put("studyCount", row.isNullAt(4) ? 0 : row.getLong(4));
                arr.add(item);
            }
            return arr;
        } catch (Exception e) {
            throw new ApiException("Failed to load user ranking", e);
        }
    }

    /**
     * Subject ranking by rating.
     */
    public JSONArray subjectRanking() {
        try {
            JSONArray arr = new JSONArray();
            Dataset<Row> df = subjectDao.subjectRanking();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                item.put("learnerCount", row.getLong(2));
                item.put("avgRating", row.isNullAt(3) ? 0 : ((Number) row.get(3)).doubleValue());
                item.put("ratingCount", row.isNullAt(4) ? 0 : row.getLong(4));
                arr.add(item);
            }
            return arr;
        } catch (Exception e) {
            throw new ApiException("Failed to load subject ranking", e);
        }
    }
}
