package edu.jxut.sft;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.*;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;

/**
 * ============================================
 *  大数据技术开发实训 — Spark数据分析微服务
 * ============================================
 *
 * 功能模块：
 *   [1] 统计分析API (GET /api/stats/*)
 *       - overview     系统综合概览（用户/科目/学习记录）
 *       - subject      各科目学习分布
 *       - user         用户学习时长TOP10
 *       - ranking      科目热度排行榜
 *
 *   [2] 机器学习API (GET /api/ml/*)
 *       - clusters           用户行为聚类分析
 *       - recommendations    热门科目推荐
 *       - hot-subjects       热门科目列表
 *       - user-recommendation  个性化推荐(传userId参数)
 *
 * 启动方式：
 *   方式A: mvn clean package exec:java (推荐开发用)
 *   方式B: java -jar target/spark-service.jar (生产部署)
 *
 * 访问地址：
 *   JavaWeb前端页面 → 调用 http://localhost:9090/api/*
 */
public class SparkServer {

    // ======================== 配置常量 ========================
    private static final int PORT = 9090;                          // 微服务端口
    private static final String DB_URL = "jdbc:mysql://127.0.0.1:3306/test"
            + "?useUnicode=true&characterEncoding=utf-8"
            + "&serverTimezone=Asia/Shanghai"
            + "&allowPublicKeyRetrieval=true"
            + "&useSSL=false";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "1234";

    private SparkSession spark;
    private Server server;

    /**
     * 初始化 SparkSession
     */
    public void initSpark() {
        spark = SparkSession.builder()
                .appName("SparkDataAnalysis")
                .master("local[*]")                    // 本地模式，使用所有CPU核心
                .config("spark.driver.memory", "512m") // 驱动内存
                .config("spark.sql.shuffle.partitions", "2") // Shuffle分区数
                .getOrCreate();
        spark.sparkContext().setLogLevel("WARN");      // 减少日志输出
        System.out.println("✅ SparkSession 初始化成功");
        System.out.println("   Spark 版本: " + spark.version());
    }

    /**
     * 启动 Jetty 嵌入式HTTP服务器，注册所有REST API Servlet
     */
    public void startServer() throws Exception {
        server = new Server(PORT);
        ServletContextHandler context = new ServletContextHandler();
        server.setHandler(context);

        // ===== 注册统计分析 API =====
        context.addServlet(new ServletHolder(new OverviewServlet()), "/api/stats/overview");
        context.addServlet(new ServletHolder(new SubjectStatsServlet()), "/api/stats/subject");
        context.addServlet(new ServletHolder(new UserStatsServlet()), "/api/stats/user");
        context.addServlet(new ServletHolder(new SubjectRankingServlet()), "/api/stats/ranking");

        // ===== 注册机器学习 API =====
        context.addServlet(new ServletHolder(new UserClusterServlet()), "/api/ml/clusters");
        context.addServlet(new ServletHolder(new RecommendationsServlet()), "/api/ml/recommendations");
        context.addServlet(new ServletHolder(new HotSubjectsServlet()), "/api/ml/hot-subjects");
        context.addServlet(new ServletHolder(new UserRecommendationServlet()), "/api/ml/user-recommendation");

        // 添加CORS跨域头（允许Java Web前端跨域调用）
        context.setInitParameter("org.eclipse.jetty.servlet.Default.dirAllowed", "false");

        server.start();

        System.out.println("\n=========================================");
        System.out.println("  🚀 Spark数据分析微服务启动成功！");
        System.out.println("  监听端口: http://localhost:" + PORT);
        System.out.println("=========================================\n");
        System.out.println("  📋 可用接口列表:");
        System.out.println("  ──────────────────────────────────────");
        System.out.println("  GET /api/stats/overview          综合概览统计");
        System.out.println("  GET /api/stats/subject           各科目学习分布");
        System.out.println("  GET /api/stats/user              用户学习时长TOP10");
        System.out.println("  GET /api/stats/ranking           科目热度排行榜");
        System.out.println("  ──────────────────────────────────────");
        System.out.println("  GET /api/ml/clusters             用户行为聚类分析");
        System.out.println("  GET /api/ml/recommendations      热门科目推荐");
        System.out.println("  GET /api/ml/hot-subjects         热门科目列表");
        System.out.println("  GET /api/ml/user-recommendation  个性化推荐(?userId=xxx)");
        System.out.println("=========================================\n");

        server.join(); // 阻塞等待服务关闭
    }

    // ======================== 工具方法 ========================

    /** 设置JSON响应头并写入数据 */
    private static void writeJson(HttpServletResponse resp, Object data) throws IOException {
        resp.setContentType("application/json;charset=UTF-8");
        resp.setCharacterEncoding("UTF-8");
        resp.getWriter().write(JSON.toJSONString(data));
    }

    /** 设置CORS跨域头 */
    private static void setCorsHeaders(HttpServletResponse resp) {
        resp.setHeader("Access-Control-Allow-Origin", "*");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
        resp.setHeader("Access-Control-Max-Age", "3600");
    }

    /** 处理预检请求(OPTIONS) */
    protected boolean handleOptions(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
            setCorsHeaders(resp);
            resp.setStatus(200);
            return true;
        }
        setCorsHeaders(resp);
        return false;
    }

    /** 从MySQL读取DataFrame的通用方法 */
    private Dataset<Row> readFromMySQL(String table, String query) {
        Properties props = new Properties();
        props.setProperty("user", DB_USER);
        props.setProperty("password", DB_PASSWORD);
        props.setProperty("driver", "com.mysql.cj.jdbc.Driver");
        if (query != null) {
            return spark.read().jdbc(DB_URL, "(" + query + ") as tmp", props);
        } else {
            return spark.read().jdbc(DB_URL, table, props);
        }
    }

    // ======================== [1] 统计分析 API ========================

    /**
     * 综合概览API
     * GET /api/stats/overview
     * 返回：用户总数、科目数量、学习记录数、人均学习次数
     */
    class OverviewServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                JSONObject result = new JSONObject(true);

                // 用户总数
                long userCount = readFromMySQL("user", "SELECT COUNT(*) AS cnt FROM user").head().getLong(0);
                result.put("userCount", userCount);

                // 科目数量
                long subjectCount = readFromMySQL("subject", "SELECT COUNT(*) AS cnt FROM subject").head().getLong(0);
                result.put("subjectCount", subjectCount);

                // 学习记录数
                long studyCount = readFromMySQL("study", "SELECT COUNT(*) AS cnt FROM study").head().getLong(0);
                result.put("studyCount", studyCount);

                // 人均学习次数
                double avgStudy = userCount > 0 ? (double) studyCount / userCount : 0;
                result.put("avgStudyPerUser", Math.round(avgStudy * 10.0) / 10.0);

                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/overview → " + userCount + "用户 | "
                        + subjectCount + "科目 | " + studyCount + "记录");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\",\"code\":500}");
            }
        }
    }

    /**
     * 科目学习分布API
     * GET /api/stats/subject
     * 返回：各科目的学习次数，降序排列前10条
     */
    class SubjectStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT s.id AS subjectId, s.name AS subjectName, " +
                                "COUNT(st.id) AS studyCount FROM subject s " +
                                "LEFT JOIN study st ON s.id = st.subject_id " +
                                "GROUP BY s.id, s.name ORDER BY studyCount DESC LIMIT 10");

                JSONArray arr = new JSONArray();
                for (Row row : df.collectAsList()) {
                    JSONObject item = new JSONObject(true);
                    item.put("subjectId", row.getInt(0));
                    item.put("subjectName", row.getString(1));
                    item.put("studyCount", row.getLong(2));
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("data", arr);
                result.put("total", arr.size());
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/subject → " + arr.size() + " 条科目记录");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 用户学习时长排行API
     * GET /api/stats/user
     * 返回：用户学习时长TOP10（降序）
     */
    class UserStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT u.id AS userId, u.real_name AS displayName, u.username AS loginName, " +
                                "COALESCE(SUM(st.duration), 0) AS totalDuration, " +
                                "COUNT(st.id) AS studyCount " +
                                "FROM user u LEFT JOIN study st ON u.username = st.creator " +
                                "GROUP BY u.id, u.real_name, u.username " +
                                "ORDER BY totalDuration DESC LIMIT 10");

                JSONArray arr = new JSONArray();
                for (Row row : df.collectAsList()) {
                    JSONObject item = new JSONObject(true);
                    item.put("userId", row.getInt(0));
                    item.put("userName", row.getString(1) != null ? row.getString(1) : row.getString(2));
                    item.put("totalDuration", ((Number) row.get(3)).longValue()); // 分钟
                    item.put("studyCount", row.getLong(4));
                    // 格式化时长为 小时:分钟
                    long totalMin = ((Number) row.get(3)).longValue();
                    int hours = (int)(totalMin / 60);
                    int mins = (int)(totalMin % 60);
                    item.put("durationText", hours > 0 ? hours+"小时"+mins+"分" : mins+"分钟");
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("data", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/user → " + arr.size() + " 位用户排行");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 科目热度排行API
     * GET /api/stats/ranking
     * 返回：科目热度得分（学习人数 × 权重），降序前10
     */
    class SubjectRankingServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT s.id, s.name, " +
                                "COUNT(DISTINCT st.creator) AS learnerCount, " +
                                "COALESCE(SUM(st.download_count), 0) AS totalDownloads, " +
                                "(COUNT(DISTINCT st.creator) * 100 + COALESCE(SUM(st.download_count), 0)) AS score " +
                                "FROM subject s LEFT JOIN study st ON s.id = st.subject_id " +
                                "GROUP BY s.id, s.name ORDER BY score DESC LIMIT 10");

                JSONArray arr = new JSONArray();
                for (Row row : df.collectAsList()) {
                    JSONObject item = new JSONObject(true);
                    item.put("subjectId", row.getInt(0));
                    item.put("name", row.getString(1));
                    item.put("learnerCount", row.getLong(2));
                    item.put("totalDownloads", ((Number) row.get(3)).longValue());
                    item.put("score", ((Number) row.get(4)).longValue());
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("data", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/ranking → " + arr.size() + " 门科目排行");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    // ======================== [2] 机器学习 API ========================

    /**
     * 用户聚类分析API
     * GET /api/ml/clusters
     * 基于活跃度比例(activity_ratio)进行规则聚类：
     *   - 活跃用户: activity_ratio > 0.5
     *   - 普通用户: activity_ratio > 0.2 且 <= 0.5
     *   - 沉默用户: activity_ratio <= 0.2 且 有学习记录
     *   - 新手用户: 无任何学习记录
     */
    class UserClusterServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                // 使用Spark SQL进行聚类分析
                // user_behavior_feature 表结构: total_study_count, total_study_hours, avg_study_duration,
                //   study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label
                Dataset<Row> df = spark.read().format("jdbc")
                        .option("url", DB_URL)
                        .option("dbtable", "user_behavior_feature")
                        .option("user", DB_USER)
                        .option("password", DB_PASSWORD)
                        .load()
                        .withColumn("cluster",
                                functions.when(functions.col("study_days").gt(15), "活跃用户")
                                        .when(functions.col("study_days").gt(5).and(
                                                functions.col("total_study_count").gt(0)), "普通用户")
                                        .when(functions.col("total_study_count").gt(0), "沉默用户")
                                        .otherwise("新手用户"));

                // 按簇聚合统计
                Dataset<Row> clusterStats = df.groupBy("cluster")
                        .agg(
                                functions.count("*").alias("count"),
                                functions.avg("total_study_count").alias("avgStudy"),
                                functions.avg("subject_count").alias("avgSubjects"),
                                functions.avg("study_days").alias("avgActivity"),
                                functions.sum("total_study_hours").alias("totalDuration")
                        )
                        .orderBy(functions.desc("count"));

                JSONArray clustersArr = new JSONArray();
                Map<String, String> colorMap = new LinkedHashMap<>();
                colorMap.put("活跃用户", "#67c23a");
                colorMap.put("普通用户", "#409eff");
                colorMap.put("沉默用户", "#e6a23c");
                colorMap.put("新手用户", "#f56c6c");

                int totalCount = 0;
                for (Row row : clusterStats.collectAsList()) {
                    JSONObject cluster = new JSONObject(true);
                    cluster.put("label", row.getString(0));
                    cluster.put("count", row.getLong(1));
                    cluster.put("avgStudy", Math.round(((Number) row.get(2)).doubleValue()));
                    cluster.put("avgSubjects", Math.round(((Number) row.get(3)).doubleValue() * 100.0) / 100.0);
                    cluster.put("avgActivity", Math.round(((Number) row.get(4)).doubleValue() * 100.0) / 100.0);
                    cluster.put("totalDuration", ((Number) row.get(5)).longValue());
                    cluster.put("color", colorMap.getOrDefault(row.getString(0), "#909399"));
                    clustersArr.add(cluster);
                    totalCount += row.getLong(1);
                }

                JSONObject result = new JSONObject(true);
                result.put("clusters", clustersArr);
                result.put("totalCount", totalCount);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/clusters → " + clustersArr.size() + " 个聚类, 共" + totalCount + "人");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 热门科目推荐API
     * GET /api/ml/recommendations
     * 推荐算法：评分人数 × 平均评分 = 推荐得分
     */
    class RecommendationsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT r.subject_id, s.name AS subjectName, " +
                                "COUNT(r.user_id) AS ratingCount, " +
                                "ROUND(AVG(r.rating), 2) AS avgRating, " +
                                "(COUNT(r.user_id) * AVG(r.rating)) AS recommendScore " +
                                "FROM user_subject_rating r " +
                                "INNER JOIN subject s ON r.subject_id = s.id " +
                                "GROUP BY r.subject_id, s.name " +
                                "ORDER BY recommendScore DESC LIMIT 10");

                JSONArray arr = new JSONArray();
                for (Row row : df.collectAsList()) {
                    JSONObject item = new JSONObject(true);
                    item.put("subjectId", row.getInt(0));
                    item.put("subjectName", row.getString(1));
                    item.put("ratingCount", row.getLong(2));
                    item.put("avgRating", ((Number) row.get(3)).doubleValue());
                    item.put("recommendScore", Math.round(((Number) row.get(4)).doubleValue()));
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("recommendations", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/recommendations → " + arr.size() + " 个热门推荐");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 热门科目API
     * GET /api/ml/hot-subjects
     * 返回：学习人数、平均评分、总评分综合排序
     */
    class HotSubjectsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT s.id, s.name, s.creator, s.category, " +
                                "COALESCE((SELECT COUNT(DISTINCT st.creator) FROM study st WHERE st.subject_id = s.id), 0) AS learnerCount, " +
                                "COALESCE((SELECT ROUND(AVG(r.rating), 2) FROM user_subject_rating r WHERE r.subject_id = s.id), 0) AS avgRating, " +
                                "COALESCE((SELECT SUM(r.rating) FROM user_subject_rating r WHERE r.subject_id = s.id), 0) AS totalRating, " +
                                "s.status " +
                                "FROM subject s ORDER BY learnerCount DESC, avgRating DESC LIMIT 15");

                JSONArray arr = new JSONArray();
                for (Row row : df.collectAsList()) {
                    JSONObject item = new JSONObject(true);
                    item.put("id", row.getInt(0));
                    item.put("name", row.getString(1));
                    item.put("creator", row.getString(2));
                    item.put("category", row.getString(3));
                    item.put("learnerCount", row.getLong(4));
                    item.put("avgRating", ((Number) row.get(5)).doubleValue());
                    item.put("totalRating", row.getLong(6));
                    item.put("status", row.getString(7));
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("hotSubjects", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/hot-subjects → " + arr.size() + " 门热门科目");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 个性化推荐API
     * GET /api/ml/user-recommendation?userId=xxx
     * 协同过滤思路：
     *   1. 找到目标用户已学习的科目
     *   2. 推荐该用户未学但高评分的科目
     *   3. 参考相似用户的偏好做补充推荐
     */
    class UserRecommendationServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                String userIdParam = req.getParameter("userId");

                JSONArray recommendations;

                if (userIdParam == null || userIdParam.trim().isEmpty()) {
                    // 无参数 → 返回默认热门推荐
                    recommendations = getDefaultRecommendations();
                } else {
                    // 有参数 → 做个性化推荐
                    recommendations = getPersonalizedRecommendations(Integer.parseInt(userIdParam.trim()));
                }

                JSONObject result = new JSONObject(true);
                result.put("recommendations", recommendations);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/user-recommendation?userId="
                        + userIdParam + " → " + recommendations.size() + " 条推荐");

            } catch (NumberFormatException e) {
                writeJson(resp, "{\"error\":\"无效的userId参数\",\"code\":400}");
            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }

        /** 默认推荐：取评分最高的前5个科目 */
        private JSONArray getDefaultRecommendations() {
            Dataset<Row> df = readFromMySQL(null,
                    "SELECT r.subject_id, s.name, s.category, " +
                            "COUNT(DISTINCT r.user_id) AS learnerCount, " +
                            "ROUND(AVG(r.rating), 1) AS avgRating " +
                            "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                            "GROUP BY r.subject_id, s.name, s.category " +
                            "HAVING AVG(r.rating) >= 4.0 " +
                            "ORDER BY avgRating DESC, learnerCount DESC LIMIT 5");

            JSONArray arr = new JSONArray();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                item.put("category", row.getString(2));
                item.put("reason", "🔥 热门好评 · " + ((Number) row.get(4)).doubleValue() + "分 · " + row.getLong(3) + "人学习");
                item.put("score", ((Number) row.get(4)).doubleValue());
                arr.add(item);
            }
            return arr;
        }

        /** 个性化推荐：排除已学，推荐高分科目 */
        private JSONArray getPersonalizedRecommendations(int targetUserId) {
            // 查询目标用户已学习的科目ID集合
            Set<Integer> learnedIds = new HashSet<>();
            try {
                Dataset<Row> learned = readFromMySQL(null,
                        "SELECT DISTINCT subject_id FROM study WHERE creator IN " +
                                "(SELECT username FROM user WHERE id=" + targetUserId + ")");
                for (Row r : learned.collectAsList()) {
                    if (!r.isNullAt(0)) learnedIds.add(r.getInt(0));
                }
            } catch (Exception e) { /* 无已学记录 */ }

            // 推荐未学的高分科目
            String excludeSql = learnedIds.isEmpty() ? "" :
                    " AND r.subject_id NOT IN (" + String.join(",", learnedIds.toString()
                            .replace("[", "").replace("]", "")) + ")";

            Dataset<Row> df = readFromMySQL(null,
                    "SELECT r.subject_id, s.name, s.category, " +
                            "ROUND(AVG(r.rating), 1) AS avgScore, " +
                            "COUNT(r.user_id) AS raterCount " +
                            "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                            "WHERE r.rating >= 4.0" + excludeSql +
                            " GROUP BY r.subject_id, s.name, s.category " +
                            "ORDER BY avgScore DESC, raterCount DESC LIMIT 5");

            JSONArray arr = new JSONArray();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                item.put("category", row.getString(2));
                double score = row.isNullAt(3) ? 0 : ((Number) row.get(3)).doubleValue();
                item.put("score", score);
                item.put("reason", "💡 根据你的兴趣推荐 · " + score + "分 · " + row.getLong(4) + "人评价");
                arr.add(item);
            }

            // 如果不足5个，补充热门推荐
            if (arr.size() < 5) {
                JSONArray defaults = getDefaultRecommendations();
                Set<String> existingNames = new HashSet<>();
                for (int i = 0; i < arr.size(); i++) {
                    existingNames.add(arr.getJSONObject(i).getString("name"));
                }
                for (int i = 0; i < defaults.size() && arr.size() < 5; i++) {
                    if (!existingNames.contains(defaults.getJSONObject(i).getString("name"))) {
                        arr.add(defaults.getJSONObject(i));
                    }
                }
            }
            return arr;
        }
    }

    // ======================== 主入口 ========================

    public static void main(String[] args) throws Exception {
        System.out.println("\n╔════════════════════════════════════════════════════╗");
        System.out.println("║    📊 大数据技术开发实训 — Spark数据分析微服务      ║");
        System.out.println("╚════════════════════════════════════════════════════╝\n");

        SparkServer app = new SparkServer();
        app.initSpark();
        app.startServer();
    }
}
