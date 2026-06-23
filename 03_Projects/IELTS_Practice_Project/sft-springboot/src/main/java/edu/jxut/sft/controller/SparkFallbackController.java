package edu.jxut.sft.controller;

import edu.jxut.sft.dto.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * Spark 微服务不可用时的本地降级接口
 * 返回与 Spark API 完全相同的数据结构，前端无需改动即可切换
 */
@RestController
@RequestMapping("/sft/local")
public class SparkFallbackController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    // ======================== 统计概览 ========================
    @GetMapping("/api/stats/overview")
    public ApiResponse overview() {
        Map<String, Object> ov = new HashMap<>();
        long userCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM `user`", Long.class);
        long subjectCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM subject", Long.class);
        long studyCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM study", Long.class);
        double avgStudy = userCount > 0 ? (double) studyCount / userCount : 0;
        ov.put("userCount", userCount);
        ov.put("subjectCount", subjectCount);
        ov.put("studyCount", studyCount);
        ov.put("avgStudyPerUser", Math.round(avgStudy * 10) / 10.0);
        return ApiResponse.success(ov);
    }

    // ======================== 科目学习分布 ========================
    @GetMapping("/api/stats/subject")
    public ApiResponse subjectDist() {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT s.name AS subjectName, COALESCE(COUNT(st.id), 0) AS studyCount " +
            "FROM subject s LEFT JOIN study st ON s.name = st.subject_name OR s.id = st.subject_id " +
            "GROUP BY s.id, s.name ORDER BY studyCount DESC");
        return ApiResponse.success(rows);
    }

    // ======================== 用户排行 ========================
    @GetMapping("/api/stats/user")
    public ApiResponse userRank(@RequestParam(defaultValue = "10") int limit) {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT u.id AS userId, u.username AS userName, u.real_name AS realName, " +
            "COALESCE(COUNT(st.id), 0) AS studyCount, '活跃' AS durationText " +
            "FROM `user` u LEFT JOIN study st ON u.username = st.creator " +
            "GROUP BY u.id, u.username, u.real_name ORDER BY studyCount DESC LIMIT ?", limit);
        return ApiResponse.success(rows);
    }

    // ======================== 科目热度排行 ========================
    @GetMapping("/api/stats/ranking")
    public ApiResponse ranking() {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT s.name AS name, COALESCE(COUNT(st.id), 0) AS score " +
            "FROM subject s LEFT JOIN study st ON s.name = st.subject_name OR s.id = st.subject_id " +
            "GROUP BY s.id, s.name ORDER BY score DESC LIMIT 10");
        return ApiResponse.success(rows);
    }

    // ======================== 用户聚类（模拟 K-Means） ========================
    @GetMapping("/api/ml/clusters")
    public ApiResponse clusters() {
        List<Map<String, Object>> users = jdbcTemplate.queryForList(
            "SELECT u.id, u.username, u.user_type, COALESCE(COUNT(st.id), 0) AS study_count " +
            "FROM `user` u LEFT JOIN study st ON u.username = st.creator GROUP BY u.id, u.username, u.user_type");

        String[] labels = {"高活跃学习者", "中等活跃者", "轻度参与者", "新注册用户"};
        String[] colors = {"#5470c6","#91cc75","#fac858","#ee6666"};
        int[] counts = {0, 0, 0, 0};
        int[] totalStudies = {0, 0, 0, 0};

        for (Map<String, Object> u : users) {
            Number sc = (Number) u.get("study_count");
            int scVal = sc != null ? sc.intValue() : 0;
            if (scVal >= 20) { counts[0]++; totalStudies[0] += scVal; }
            else if (scVal >= 5) { counts[1]++; totalStudies[1] += scVal; }
            else if (scVal >= 1) { counts[2]++; totalStudies[2] += scVal; }
            else { counts[3]++; }
        }

        List<Map<String, Object>> clusterList = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            Map<String, Object> c = new LinkedHashMap<>();
            c.put("label", labels[i]);
            c.put("color", colors[i]);
            c.put("count", counts[i]);
            c.put("avgStudy", counts[i] > 0 ? Math.round((double)totalStudies[i]/counts[i]*10)/10.0 : 0);
            c.put("avgSubjects", Math.round(33.0 * (4-i)/4 * 10)/10.0); // 模拟值
            c.put("avgActivity", counts[i] > 0 ? "高" : "低");
            clusterList.add(c);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("clusters", clusterList);
        result.put("totalCount", users.size());
        return ApiResponse.success(result);
    }

    // ======================== 热门推荐 ========================
    @GetMapping("/api/ml/recommendations")
    public ApiResponse recommendations() {
        List<Map<String, Object>> items = jdbcTemplate.queryForList(
            "SELECT s.name, s.creator, COALESCE(COUNT(st.id), 0) as learner_count, " +
            "COALESCE(AVG(usr.rating), 4.5) as avg_rating " +
            "FROM subject s " +
            "LEFT JOIN study st ON s.name = st.subject_name OR s.id = st.subject_id " +
            "LEFT JOIN user_subject_rating usr ON s.id = usr.subject_id " +
            "GROUP BY s.id, s.name, s.creator ORDER BY learner_count DESC LIMIT 8");

        List<Map<String, Object>> recs = new ArrayList<>();
        for (Map<String, Object> item : items) {
            Map<String, Object> rec = new LinkedHashMap<>();
            rec.put("name", item.get("name"));
            rec.put("category", "热门科目");
            Number avgR = (Number) item.get("avg_rating");
            rec.put("score", avgR != null ? avgR.doubleValue() : 4.5);
            rec.put("reason", "基于用户学习热度推荐");
            rec.put("avgRating", avgR != null ? avgR.doubleValue() : 4.5);
            recs.add(rec);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("recommendations", recs);
        return ApiResponse.success(result);
    }

    @GetMapping("/api/ml/user-recommendation")
    public ApiResponse userRecommendation(@RequestParam(defaultValue = "1") int userId) {
        return recommendations();
    }

    // ======================== 热门科目 ========================
    @GetMapping("/api/ml/hot-subjects")
    public ApiResponse hotSubjects() {
        List<Map<String, Object>> items = jdbcTemplate.queryForList(
            "SELECT s.name, s.creator, s.status, " +
            "COALESCE(COUNT(st.id), 0) as learner_count, " +
            "COALESCE(SUM(COALESCE(usr.rating, 45)), 0) as total_rating, " +
            "COALESCE(AVG(usr.rating), 45) as avg_rating " +
            "FROM subject s " +
            "LEFT JOIN study st ON s.name = st.subject_name OR s.id = st.subject_id " +
            "LEFT JOIN user_subject_rating usr ON s.id = usr.subject_id " +
            "GROUP BY s.id, s.name, s.creator, s.status ORDER BY learner_count DESC");

        List<Map<String, Object>> hotList = new ArrayList<>();
        for (Map<String, Object> item : items) {
            Map<String, Object> h = new LinkedHashMap<>();
            h.put("name", item.get("name"));
            h.put("creator", item.get("creator"));
            h.put("learnerCount", ((Number)item.get("learner_count")).intValue());
            h.put("totalRating", ((Number)item.get("total_rating")).intValue());
            Number ar = (Number) item.get("avg_rating");
            h.put("avgRating", ar != null ? Math.round(ar.doubleValue()*10)/10.0 : 4.5);
            hotList.add(h);
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("hotSubjects", hotList);
        return ApiResponse.success(result);
    }
}
