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
 *  澶ф暟鎹妧鏈紑鍙戝疄璁?鈥?Spark鏁版嵁鍒嗘瀽寰湇鍔?
 * ============================================
 *
 * 鍔熻兘妯″潡锛?
 *   [1] 缁熻鍒嗘瀽API (GET /api/stats/*)
 *       - overview     绯荤粺缁煎悎姒傝锛堢敤鎴?绉戠洰/瀛︿範璁板綍锛?
 *       - subject      鍚勭鐩涔犲垎甯?
 *       - user         鐢ㄦ埛瀛︿範鏃堕暱TOP10
 *       - ranking      绉戠洰鐑害鎺掕姒?
 *
 *   [2] 鏈哄櫒瀛︿範API (GET /api/ml/*)
 *       - clusters           鐢ㄦ埛琛屼负鑱氱被鍒嗘瀽
 *       - recommendations    鐑棬绉戠洰鎺ㄨ崘
 *       - hot-subjects       鐑棬绉戠洰鍒楄〃
 *       - user-recommendation  涓€у寲鎺ㄨ崘(浼爑serId鍙傛暟)
 *
 * 鍚姩鏂瑰紡锛?
 *   鏂瑰紡A: mvn clean package exec:java (鎺ㄨ崘寮€鍙戠敤)
 *   鏂瑰紡B: java -jar target/spark-service.jar (鐢熶骇閮ㄧ讲)
 *
 * 璁块棶鍦板潃锛?
 *   JavaWeb鍓嶇椤甸潰 鈫?璋冪敤 http://localhost:9090/api/*
 */
public class SparkServer {

    // ======================== 閰嶇疆甯搁噺 ========================
    private static final int PORT = 9090;                          // 寰湇鍔＄鍙?
    private static final String DB_URL = "jdbc:mysql://127.0.0.1:3306/test"
            + "?useUnicode=true&characterEncoding=utf-8"
            + "&serverTimezone=Asia/Shanghai"
            + "&allowPublicKeyRetrieval=true"
            + "&useSSL=false";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "123456";

    private SparkSession spark;
    private Server server;

    /**
     * 鍒濆鍖?SparkSession
     */
    public void initSpark() {
        spark = SparkSession.builder()
                .appName("SparkDataAnalysis")
                .master("local[*]")                    // 鏈湴妯″紡锛屼娇鐢ㄦ墍鏈塁PU鏍稿績
                .config("spark.driver.memory", "512m") // 椹卞姩鍐呭瓨
                .config("spark.sql.shuffle.partitions", "2") // Shuffle鍒嗗尯鏁?
                .getOrCreate();
        spark.sparkContext().setLogLevel("WARN");      // 鍑忓皯鏃ュ織杈撳嚭
        System.out.println("鉁?SparkSession 鍒濆鍖栨垚鍔?);
        System.out.println("   Spark 鐗堟湰: " + spark.version());
    }

    /**
     * 鍚姩 Jetty 宓屽叆寮廐TTP鏈嶅姟鍣紝娉ㄥ唽鎵€鏈塕EST API Servlet
     */
    public void startServer() throws Exception {
        server = new Server(PORT);
        ServletContextHandler context = new ServletContextHandler();
        server.setHandler(context);

        // ===== 娉ㄥ唽缁熻鍒嗘瀽 API =====
        context.addServlet(new ServletHolder(new OverviewServlet()), "/api/stats/overview");
        context.addServlet(new ServletHolder(new SubjectStatsServlet()), "/api/stats/subject");
        context.addServlet(new ServletHolder(new UserStatsServlet()), "/api/stats/user");
        context.addServlet(new ServletHolder(new SubjectRankingServlet()), "/api/stats/ranking");

        // ===== 娉ㄥ唽鏈哄櫒瀛︿範 API =====
        context.addServlet(new ServletHolder(new UserClusterServlet()), "/api/ml/clusters");
        context.addServlet(new ServletHolder(new RecommendationsServlet()), "/api/ml/recommendations");
        context.addServlet(new ServletHolder(new HotSubjectsServlet()), "/api/ml/hot-subjects");
        context.addServlet(new ServletHolder(new UserRecommendationServlet()), "/api/ml/user-recommendation");

        // 娣诲姞CORS璺ㄥ煙澶达紙鍏佽Java Web鍓嶇璺ㄥ煙璋冪敤锛?
        context.setInitParameter("org.eclipse.jetty.servlet.Default.dirAllowed", "false");

        server.start();

        System.out.println("\n=========================================");
        System.out.println("  馃殌 Spark鏁版嵁鍒嗘瀽寰湇鍔″惎鍔ㄦ垚鍔燂紒");
        System.out.println("  鐩戝惉绔彛: http://localhost:" + PORT);
        System.out.println("=========================================\n");
        System.out.println("  馃搵 鍙敤鎺ュ彛鍒楄〃:");
        System.out.println("  鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€");
        System.out.println("  GET /api/stats/overview          缁煎悎姒傝缁熻");
        System.out.println("  GET /api/stats/subject           鍚勭鐩涔犲垎甯?);
        System.out.println("  GET /api/stats/user              鐢ㄦ埛瀛︿範鏃堕暱TOP10");
        System.out.println("  GET /api/stats/ranking           绉戠洰鐑害鎺掕姒?);
        System.out.println("  鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€");
        System.out.println("  GET /api/ml/clusters             鐢ㄦ埛琛屼负鑱氱被鍒嗘瀽");
        System.out.println("  GET /api/ml/recommendations      鐑棬绉戠洰鎺ㄨ崘");
        System.out.println("  GET /api/ml/hot-subjects         鐑棬绉戠洰鍒楄〃");
        System.out.println("  GET /api/ml/user-recommendation  涓€у寲鎺ㄨ崘(?userId=xxx)");
        System.out.println("=========================================\n");

        server.join(); // 闃诲绛夊緟鏈嶅姟鍏抽棴
    }

    // ======================== 宸ュ叿鏂规硶 ========================

    /** 璁剧疆JSON鍝嶅簲澶村苟鍐欏叆鏁版嵁 */
    private static void writeJson(HttpServletResponse resp, Object data) throws IOException {
        resp.setContentType("application/json;charset=UTF-8");
        resp.setCharacterEncoding("UTF-8");
        resp.getWriter().write(JSON.toJSONString(data));
    }

    /** 璁剧疆CORS璺ㄥ煙澶?*/
    private static void setCorsHeaders(HttpServletResponse resp) {
        resp.setHeader("Access-Control-Allow-Origin", "*");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
        resp.setHeader("Access-Control-Max-Age", "3600");
    }

    /** 澶勭悊棰勬璇锋眰(OPTIONS) */
    protected boolean handleOptions(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
            setCorsHeaders(resp);
            resp.setStatus(200);
            return true;
        }
        setCorsHeaders(resp);
        return false;
    }

    /** 浠嶮ySQL璇诲彇DataFrame鐨勯€氱敤鏂规硶 */
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

    // ======================== [1] 缁熻鍒嗘瀽 API ========================

    /**
     * 缁煎悎姒傝API
     * GET /api/stats/overview
     * 杩斿洖锛氱敤鎴锋€绘暟銆佺鐩暟閲忋€佸涔犺褰曟暟銆佷汉鍧囧涔犳鏁?
     */
    class OverviewServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                JSONObject result = new JSONObject(true);

                // 鐢ㄦ埛鎬绘暟
                long userCount = readFromMySQL("user", "SELECT COUNT(*) AS cnt FROM user").head().getLong(0);
                result.put("userCount", userCount);

                // 绉戠洰鏁伴噺
                long subjectCount = readFromMySQL("subject", "SELECT COUNT(*) AS cnt FROM subject").head().getLong(0);
                result.put("subjectCount", subjectCount);

                // 瀛︿範璁板綍鏁?
                long studyCount = readFromMySQL("study", "SELECT COUNT(*) AS cnt FROM study").head().getLong(0);
                result.put("studyCount", studyCount);

                // 浜哄潎瀛︿範娆℃暟
                double avgStudy = userCount > 0 ? (double) studyCount / userCount : 0;
                result.put("avgStudyPerUser", Math.round(avgStudy * 10.0) / 10.0);

                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/overview 鈫?" + userCount + "鐢ㄦ埛 | "
                        + subjectCount + "绉戠洰 | " + studyCount + "璁板綍");

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\",\"code\":500}");
            }
        }
    }

    /**
     * 绉戠洰瀛︿範鍒嗗竷API
     * GET /api/stats/subject
     * 杩斿洖锛氬悇绉戠洰鐨勫涔犳鏁帮紝闄嶅簭鎺掑垪鍓?0鏉?
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
                System.out.println("[API] /stats/subject 鈫?" + arr.size() + " 鏉＄鐩褰?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 鐢ㄦ埛瀛︿範鏃堕暱鎺掕API
     * GET /api/stats/user
     * 杩斿洖锛氱敤鎴峰涔犳椂闀縏OP10锛堥檷搴忥級
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
                    item.put("totalDuration", ((Number) row.get(3)).longValue()); // 鍒嗛挓
                    item.put("studyCount", row.getLong(4));
                    // 鏍煎紡鍖栨椂闀夸负 灏忔椂:鍒嗛挓
                    long totalMin = ((Number) row.get(3)).longValue();
                    int hours = (int)(totalMin / 60);
                    int mins = (int)(totalMin % 60);
                    item.put("durationText", hours > 0 ? hours+"灏忔椂"+mins+"鍒? : mins+"鍒嗛挓");
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("data", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /stats/user 鈫?" + arr.size() + " 浣嶇敤鎴锋帓琛?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 绉戠洰鐑害鎺掕API
     * GET /api/stats/ranking
     * 杩斿洖锛氱鐩儹搴﹀緱鍒嗭紙瀛︿範浜烘暟 脳 鏉冮噸锛夛紝闄嶅簭鍓?0
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
                System.out.println("[API] /stats/ranking 鈫?" + arr.size() + " 闂ㄧ鐩帓琛?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    // ======================== [2] 鏈哄櫒瀛︿範 API ========================

    /**
     * 鐢ㄦ埛鑱氱被鍒嗘瀽API
     * GET /api/ml/clusters
     * 鍩轰簬娲昏穬搴︽瘮渚?activity_ratio)杩涜瑙勫垯鑱氱被锛?
     *   - 娲昏穬鐢ㄦ埛: activity_ratio > 0.5
     *   - 鏅€氱敤鎴? activity_ratio > 0.2 涓?<= 0.5
     *   - 娌夐粯鐢ㄦ埛: activity_ratio <= 0.2 涓?鏈夊涔犺褰?
     *   - 鏂版墜鐢ㄦ埛: 鏃犱换浣曞涔犺褰?
     */
    class UserClusterServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                // 浣跨敤Spark SQL杩涜鑱氱被鍒嗘瀽
                // user_behavior_feature 琛ㄧ粨鏋? total_study_count, total_study_hours, avg_study_duration,
                //   study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label
                Dataset<Row> df = spark.read().format("jdbc")
                        .option("url", DB_URL)
                        .option("dbtable", "user_behavior_feature")
                        .option("user", DB_USER)
                        .option("password", DB_PASSWORD)
                        .load()
                        .withColumn("cluster",
                                functions.when(functions.col("study_days").gt(15), "娲昏穬鐢ㄦ埛")
                                        .when(functions.col("study_days").gt(5).and(
                                                functions.col("total_study_count").gt(0)), "鏅€氱敤鎴?)
                                        .when(functions.col("total_study_count").gt(0), "娌夐粯鐢ㄦ埛")
                                        .otherwise("鏂版墜鐢ㄦ埛"));

                // 鎸夌皣鑱氬悎缁熻
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
                colorMap.put("娲昏穬鐢ㄦ埛", "#67c23a");
                colorMap.put("鏅€氱敤鎴?, "#409eff");
                colorMap.put("娌夐粯鐢ㄦ埛", "#e6a23c");
                colorMap.put("鏂版墜鐢ㄦ埛", "#f56c6c");

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
                System.out.println("[API] /ml/clusters 鈫?" + clustersArr.size() + " 涓仛绫? 鍏? + totalCount + "浜?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 鐑棬绉戠洰鎺ㄨ崘API
     * GET /api/ml/recommendations
     * 鎺ㄨ崘绠楁硶锛氳瘎鍒嗕汉鏁?脳 骞冲潎璇勫垎 = 鎺ㄨ崘寰楀垎
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
                System.out.println("[API] /ml/recommendations 鈫?" + arr.size() + " 涓儹闂ㄦ帹鑽?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 鐑棬绉戠洰API
     * GET /api/ml/hot-subjects
     * 杩斿洖锛氬涔犱汉鏁般€佸钩鍧囪瘎鍒嗐€佹€昏瘎鍒嗙患鍚堟帓搴?
     */
    class HotSubjectsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                Dataset<Row> df = readFromMySQL(null,
                        "SELECT s.id, s.name, s.creator, " +
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
                    item.put("learnerCount", ((Number) row.get(3)).longValue());
                    item.put("avgRating", ((Number) row.get(4)).doubleValue());
                    item.put("totalRating", ((Number) row.get(5)).longValue());
                    item.put("status", row.getString(6));
                    arr.add(item);
                }

                JSONObject result = new JSONObject(true);
                result.put("hotSubjects", arr);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/hot-subjects 鈫?" + arr.size() + " 闂ㄧ儹闂ㄧ鐩?);

            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /**
     * 涓€у寲鎺ㄨ崘API
     * GET /api/ml/user-recommendation?userId=xxx
     * 鍗忓悓杩囨护鎬濊矾锛?
     *   1. 鎵惧埌鐩爣鐢ㄦ埛宸插涔犵殑绉戠洰
     *   2. 鎺ㄨ崘璇ョ敤鎴锋湭瀛︿絾楂樿瘎鍒嗙殑绉戠洰
     *   3. 鍙傝€冪浉浼肩敤鎴风殑鍋忓ソ鍋氳ˉ鍏呮帹鑽?
     */
    class UserRecommendationServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
            if (handleOptions(req, resp)) return;

            try {
                String userIdParam = req.getParameter("userId");

                JSONArray recommendations;

                if (userIdParam == null || userIdParam.trim().isEmpty()) {
                    // 鏃犲弬鏁?鈫?杩斿洖榛樿鐑棬鎺ㄨ崘
                    recommendations = getDefaultRecommendations();
                } else {
                    // 鏈夊弬鏁?鈫?鍋氫釜鎬у寲鎺ㄨ崘
                    recommendations = getPersonalizedRecommendations(Integer.parseInt(userIdParam.trim()));
                }

                JSONObject result = new JSONObject(true);
                result.put("recommendations", recommendations);
                result.put("code", 200);
                writeJson(resp, result);
                System.out.println("[API] /ml/user-recommendation?userId="
                        + userIdParam + " 鈫?" + recommendations.size() + " 鏉℃帹鑽?);

            } catch (NumberFormatException e) {
                writeJson(resp, "{\"error\":\"鏃犳晥鐨剈serId鍙傛暟\",\"code\":400}");
            } catch (Exception e) {
                e.printStackTrace();
                writeJson(resp, "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }

        /** 榛樿鎺ㄨ崘锛氬彇璇勫垎鏈€楂樼殑鍓?涓鐩?*/
        private JSONArray getDefaultRecommendations() {
            Dataset<Row> df = readFromMySQL(null,
                    "SELECT r.subject_id, s.name, " +
                            "COUNT(DISTINCT r.user_id) AS learnerCount, " +
                            "ROUND(AVG(r.rating), 1) AS avgRating " +
                            "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                            "GROUP BY r.subject_id, s.name " +
                            "HAVING AVG(r.rating) >= 4.0 " +
                            "ORDER BY avgRating DESC, learnerCount DESC LIMIT 5");

            JSONArray arr = new JSONArray();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                item.put("reason", "馃敟 鐑棬濂借瘎 路 " + ((Number) row.get(3)).doubleValue() + "鍒?路 " + row.getLong(2) + "浜哄涔?);
                item.put("score", ((Number) row.get(3)).doubleValue());
                arr.add(item);
            }
            return arr;
        }

        /** 涓€у寲鎺ㄨ崘锛氭帓闄ゅ凡瀛︼紝鎺ㄨ崘楂樺垎绉戠洰 */
        private JSONArray getPersonalizedRecommendations(int targetUserId) {
            // 鏌ヨ鐩爣鐢ㄦ埛宸插涔犵殑绉戠洰ID闆嗗悎
            Set<Integer> learnedIds = new HashSet<>();
            try {
                Dataset<Row> learned = readFromMySQL(null,
                        "SELECT DISTINCT subject_id FROM study WHERE creator IN " +
                                "(SELECT username FROM user WHERE id=" + targetUserId + ")");
                for (Row r : learned.collectAsList()) {
                    if (!r.isNullAt(0)) learnedIds.add(r.getInt(0));
                }
            } catch (Exception e) { /* 鏃犲凡瀛﹁褰?*/ }

            // 鎺ㄨ崘鏈鐨勯珮鍒嗙鐩?
            String excludeSql = learnedIds.isEmpty() ? "" :
                    " AND r.subject_id NOT IN (" + String.join(",", learnedIds.toString()
                            .replace("[", "").replace("]", "")) + ")";

            Dataset<Row> df = readFromMySQL(null,
                    "SELECT r.subject_id, s.name, " +
                            "ROUND(AVG(r.rating), 1) AS avgScore, " +
                            "COUNT(r.user_id) AS raterCount " +
                            "FROM user_subject_rating r INNER JOIN subject s ON r.subject_id = s.id " +
                            "WHERE r.rating >= 4.0" + excludeSql +
                            " GROUP BY r.subject_id, s.name " +
                            "ORDER BY avgScore DESC, raterCount DESC LIMIT 5");

            JSONArray arr = new JSONArray();
            for (Row row : df.collectAsList()) {
                JSONObject item = new JSONObject(true);
                item.put("subjectId", row.getInt(0));
                item.put("name", row.getString(1));
                double score = row.isNullAt(2) ? 0 : ((Number) row.get(2)).doubleValue();
                item.put("score", score);
                item.put("reason", "馃挕 鏍规嵁浣犵殑鍏磋叮鎺ㄨ崘 路 " + score + "鍒?路 " + row.getLong(3) + "浜鸿瘎浠?);
                arr.add(item);
            }

            // 濡傛灉涓嶈冻5涓紝琛ュ厖鐑棬鎺ㄨ崘
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

    // ======================== 涓诲叆鍙?========================

    public static void main(String[] args) throws Exception {
        System.out.println("\n鈺斺晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晽");
        System.out.println("鈺?   馃搳 澶ф暟鎹妧鏈紑鍙戝疄璁?鈥?Spark鏁版嵁鍒嗘瀽寰湇鍔?     鈺?);
        System.out.println("鈺氣晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨暆\n");

        SparkServer app = new SparkServer();
        app.initSpark();
        app.startServer();
    }
}
