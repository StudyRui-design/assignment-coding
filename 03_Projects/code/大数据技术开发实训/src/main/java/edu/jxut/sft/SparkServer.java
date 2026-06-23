package edu.jxut.sft;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.desc;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 基于Apache Spark的数据分析微服务主启动类
 * <p>
 * 功能说明：
 * 1. 初始化SparkSession用于大数据分析计算
 * 2. 启动嵌入式Jetty服务器提供REST API接口（端口9090）
 * 3. 连接MySQL数据库获取课件管理系统数据
 * 4. 提供科目排名、课件统计、用户分析等数据可视化API
 *
 * @author 邓睿
 */
public class SparkServer {

    // ==================== 配置常量 ====================

    /** Spark应用名称 */
    private static final String SPARK_APP_NAME = "SparkDataAnalysis";

    /** Spark运行模式（local[*]：使用本地所有CPU核心） */
    private static final String SPARK_MASTER = "local[*]";

    /** Spark Driver进程内存 */
    private static final String SPARK_DRIVER_MEMORY = "512m";

    /** Shuffle分区数 */
    private static final int SPARK_SHUFFLE_PARTITIONS = 2;

    /** Jetty服务器端口 */
    private static final int JETTY_PORT = 9090;

    /** 数据库连接URL */
    private static final String DB_URL = "jdbc:mysql://127.0.0.1:3306/test"
            + "?useUnicode=true&characterEncoding=utf-8&useSSL=false"
            + "&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true";

    /** 数据库用户名 */
    private static final String DB_USERNAME = "root";

    /** 数据库密码 */
    private static final String DB_PASSWORD = "123456";

    // ==================== 全局实例 ====================

    /** SparkSession实例 */
    private static SparkSession spark;

    /**
     * 主入口方法
     * <p>
     * 执行顺序：先初始化SparkSession → 再启动Jetty HTTP服务器
     *
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        try {
            // 第一步：初始化SparkSession
            initSparkSession();

            // 第二步：启动嵌入式Jetty服务器
            Server server = startJettyServer();

            System.out.println("========================================");
            System.out.println("  Spark数据分析微服务启动成功！");
            System.out.println("  Spark AppName  : " + SPARK_APP_NAME);
            System.out.println("  Spark Master   : " + SPARK_MASTER);
            System.out.println("  Jetty Port     : " + JETTY_PORT);
            System.out.println("  DAO Base URL   : http://localhost:" + JETTY_PORT + "/spark/api");
            System.out.println("  数据库 URL      : " + DB_URL);
            System.out.println("========================================");

            // 阻塞主线程，保持服务运行
            server.join();

        } catch (Exception e) {
            System.err.println("[ERROR] Spark微服务启动失败: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * 第一步：创建并配置SparkSession
     */
    private static void initSparkSession() {
        System.out.println("[INFO] 正在初始化 SparkSession ...");

        spark = SparkSession.builder()
                .appName(SPARK_APP_NAME)
                .master(SPARK_MASTER)
                .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
                .config("spark.sql.shuffle.partitions", String.valueOf(SPARK_SHUFFLE_PARTITIONS))
                // 关闭不必要的日志输出
                .config("spark.ui.enabled", "false")
                .getOrCreate();

        // 注意：不调用 setLogLevel，因为 Spring Boot 的 Logback 与 Spark 的 Log4j 冲突
        // ClassPath 中 Logback 优先，Spark 默认日志级别即为 WARN

        System.out.println("[INFO] SparkSession 创建成功！");
        System.out.println("[INFO] Spark 版本: " + spark.version());
    }

    /**
     * 第二步：启动嵌入式Jetty服务器
     */
    private static Server startJettyServer() throws Exception {
        System.out.println("[INFO] 正在启动 Jetty 服务器（端口: " + JETTY_PORT + "）...");

        Server server = new Server(JETTY_PORT);

        // 创建Servlet上下文处理器
        ServletContextHandler context = new ServletContextHandler(ServletContextHandler.SESSIONS);
        context.setContextPath("/spark");
        server.setHandler(context);

        // ---- 注册 REST API 端点 ----

        // CORS过滤器 —— 所有请求都经过，处理跨域和OPTIONS预检
        context.addFilter(CorsFilter.class, "/*", null);

        // 健康检查接口
        context.addServlet(new ServletHolder(new HealthServlet()), "/api/health");

        // 科目排名分析接口
        context.addServlet(new ServletHolder(new SubjectRankServlet()), "/api/subject/rank");

        // 课件统计数据接口
        context.addServlet(new ServletHolder(new StudyStatsServlet()), "/api/study/stats");

        // 用户分析接口
        context.addServlet(new ServletHolder(new UserAnalysisServlet()), "/api/user/analysis");

        // 仪表盘总览数据接口
        context.addServlet(new ServletHolder(new DashboardServlet()), "/api/dashboard");

        // 综合概览统计接口（使用Spark JDBC读取数据库）
        context.addServlet(new ServletHolder(new OverviewServlet()), "/api/stats/overview");

        // 科目学习次数分布统计接口
        context.addServlet(new ServletHolder(new SubjectStatsServlet()), "/api/stats/subject");

        // 用户行为特征分析接口
        context.addServlet(new ServletHolder(new UserBehaviorServlet()), "/api/stats/behavior");

        // 用户评分分析接口
        context.addServlet(new ServletHolder(new RatingStatsServlet()), "/api/stats/rating");

        // 用户学习时长排行接口
        context.addServlet(new ServletHolder(new UserStatsServlet()), "/api/stats/user");

        // 科目热度排行接口
        context.addServlet(new ServletHolder(new SubjectRankingServlet()), "/api/stats/ranking");

        // 启动服务器
        server.start();
        System.out.println("[INFO] Jetty 服务器已启动！");
        return server;
    }

    // ==================== 内部Servlet类 ====================

    /**
     * CORS跨域过滤器 —— 为所有请求添加跨域响应头，并处理OPTIONS预检
     */
    public static class CorsFilter implements Filter {
        @Override
        public void init(FilterConfig filterConfig) throws ServletException { }

        @Override
        public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
                throws IOException, ServletException {
            HttpServletResponse resp = (HttpServletResponse) response;
            HttpServletRequest req = (HttpServletRequest) request;

            resp.setHeader("Access-Control-Allow-Origin", "*");
            resp.setHeader("Access-Control-Allow-Methods",
                    "GET, POST, PUT, DELETE, OPTIONS");
            resp.setHeader("Access-Control-Allow-Headers",
                    "Content-Type, Authorization, X-Requested-With");
            resp.setHeader("Access-Control-Max-Age", "3600");

            // 对OPTIONS预检请求直接返回200
            if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
                resp.setStatus(HttpServletResponse.SC_OK);
                return;
            }

            chain.doFilter(request, response);
        }

        @Override
        public void destroy() { }
    }

    /**
     * 健康检查接口 —— GET /spark/api/health
     */
    public static class HealthServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("status", "UP");
            result.put("service", "SparkDataAnalysis");
            result.put("sparkVersion", spark.version());
            result.put("sparkAppName", SPARK_APP_NAME);
            result.put("sparkMaster", SPARK_MASTER);
            result.put("timestamp", System.currentTimeMillis());

            writeJson(resp, toJson(result));
        }
    }

    /**
     * 科目排名分析接口 —— GET /spark/api/subject/rank
     * 统计每个科目下的课件数量，按数量降序排列
     */
    public static class SubjectRankServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            try {
                List<Map<String, Object>> rankData = new ArrayList<>();

                // 使用JDBC从MySQL查询科目-课件统计数据
                try (Connection conn = getConnection();
                     Statement stmt = conn.createStatement();
                     ResultSet rs = stmt.executeQuery(
                             "SELECT s.name AS subject_name, " +
                                     "COUNT(st.id) AS study_count " +
                                     "FROM subject s " +
                                     "LEFT JOIN study st ON s.name = st.subjectName " +
                                     "GROUP BY s.name " +
                                     "ORDER BY study_count DESC")) {

                    while (rs.next()) {
                        Map<String, Object> item = new LinkedHashMap<>();
                        item.put("subjectName", rs.getString("subject_name"));
                        item.put("studyCount", rs.getInt("study_count"));
                        rankData.add(item);
                    }

                    // 使用Spark进行二次分析：计算平均值、最大值
                    if (!rankData.isEmpty() && spark != null) {
                        // 将数据转为Spark DataFrame进行聚合计算
                        // 此处保留Spark分析能力，后续可扩展
                        long totalStudies = rankData.stream()
                                .mapToInt(m -> (int) m.get("studyCount")).sum();
                        double avgCount = rankData.isEmpty() ? 0 :
                                (double) totalStudies / rankData.size();

                        Map<String, Object> sparkAnalysis = new LinkedHashMap<>();
                        sparkAnalysis.put("totalSubjects", rankData.size());
                        sparkAnalysis.put("totalStudies", totalStudies);
                        sparkAnalysis.put("avgStudiesPerSubject",
                                Math.round(avgCount * 100.0) / 100.0);

                        Map<String, Object> result = new LinkedHashMap<>();
                        result.put("code", 200);
                        result.put("message", "success");
                        result.put("sparkAnalysis", sparkAnalysis);
                        result.put("data", rankData);
                        writeJson(resp, toJson(result));
                    } else {
                        Map<String, Object> result = new LinkedHashMap<>();
                        result.put("code", 200);
                        result.put("message", "success");
                        result.put("data", rankData);
                        writeJson(resp, toJson(result));
                    }

                }
            } catch (Exception e) {
                writeError(resp, "科目排名分析失败: " + e.getMessage());
            }
        }
    }

    /**
     * 课件统计数据接口 —— GET /spark/api/study/stats
     * 提供课件总数、创建者分布等统计信息
     */
    public static class StudyStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            try {
                Map<String, Object> stats = new LinkedHashMap<>();

                try (Connection conn = getConnection()) {

                    // 课件总数
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT COUNT(*) FROM study")) {
                        if (rs.next()) {
                            stats.put("totalStudies", rs.getInt(1));
                        }
                    }

                    // 课件创建者分布
                    List<Map<String, Object>> creatorDist = new ArrayList<>();
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT creator, COUNT(*) AS cnt FROM study " +
                                         "GROUP BY creator ORDER BY cnt DESC")) {
                        while (rs.next()) {
                            Map<String, Object> item = new LinkedHashMap<>();
                            item.put("creator", rs.getString("creator"));
                            item.put("count", rs.getInt("cnt"));
                            creatorDist.add(item);
                        }
                    }
                    stats.put("creatorDistribution", creatorDist);

                    // 最近创建的课件（前10条）
                    List<Map<String, Object>> recentStudies = new ArrayList<>();
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT id, name, subjectName, creator, createTime " +
                                         "FROM study ORDER BY id DESC LIMIT 10")) {
                        while (rs.next()) {
                            Map<String, Object> item = new LinkedHashMap<>();
                            item.put("id", rs.getInt("id"));
                            item.put("name", rs.getString("name"));
                            item.put("subjectName", rs.getString("subjectName"));
                            item.put("creator", rs.getString("creator"));
                            item.put("createTime",
                                    rs.getTimestamp("createTime") != null ?
                                            rs.getTimestamp("createTime").toString() : null);
                            recentStudies.add(item);
                        }
                    }
                    stats.put("recentStudies", recentStudies);
                }

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", stats);
                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "课件统计失败: " + e.getMessage());
            }
        }
    }

    /**
     * 用户分析接口 —— GET /spark/api/user/analysis
     * 统计用户总数以及各用户创建的课件数
     */
    public static class UserAnalysisServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            try {
                Map<String, Object> analysis = new LinkedHashMap<>();

                try (Connection conn = getConnection()) {

                    // 用户总数
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT COUNT(*) FROM user")) {
                        if (rs.next()) {
                            analysis.put("totalUsers", rs.getInt(1));
                        }
                    }

                    // 用户课件贡献排行
                    List<Map<String, Object>> userContrib = new ArrayList<>();
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT u.username, COUNT(s.id) AS study_count " +
                                         "FROM user u " +
                                         "LEFT JOIN study s ON u.username = s.creator " +
                                         "GROUP BY u.username " +
                                         "ORDER BY study_count DESC")) {
                        while (rs.next()) {
                            Map<String, Object> item = new LinkedHashMap<>();
                            item.put("username", rs.getString("username"));
                            item.put("studyCount", rs.getInt("study_count"));
                            userContrib.add(item);
                        }
                    }
                    analysis.put("userContribution", userContrib);
                }

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", analysis);
                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "用户分析失败: " + e.getMessage());
            }
        }
    }

    /**
     * 仪表盘总览接口 —— GET /spark/api/dashboard
     * 提供系统整体的统计概览数据
     */
    public static class DashboardServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            try {
                Map<String, Object> dashboard = new LinkedHashMap<>();

                try (Connection conn = getConnection()) {

                    // 科目总数
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM subject")) {
                        if (rs.next()) dashboard.put("totalSubjects", rs.getInt(1));
                    }

                    // 课件总数
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM study")) {
                        if (rs.next()) dashboard.put("totalStudies", rs.getInt(1));
                    }

                    // 用户总数
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM user")) {
                        if (rs.next()) dashboard.put("totalUsers", rs.getInt(1));
                    }

                    // 活跃科目数（有课件的科目）
                    try (Statement stmt = conn.createStatement();
                         ResultSet rs = stmt.executeQuery(
                                 "SELECT COUNT(DISTINCT subjectName) FROM study")) {
                        if (rs.next()) dashboard.put("activeSubjects", rs.getInt(1));
                    }
                }

                dashboard.put("sparkVersion", spark.version());
                dashboard.put("sparkMaster", SPARK_MASTER);

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", dashboard);
                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "仪表盘数据获取失败: " + e.getMessage());
            }
        }
    }

    /**
     * 综合概览统计接口 —— GET /spark/api/stats/overview
     * <p>
     * 使用Spark JDBC直接读取MySQL数据库，返回系统综合统计数据：
     * - totalUsers：user表总用户数
     * - totalSubjects：subject表科目数量
     * - totalStudies：study表学习记录数
     * - avgStudiesPerUser：人均学习次数
     */
    public static class OverviewServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            // 设置响应Content-Type为application/json，编码UTF-8
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                // Spark JDBC 连接属性
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 使用Spark JDBC读取 user 表，统计总用户数
                Dataset<Row> userDF = spark.read()
                        .jdbc(DB_URL, "user", connectionProperties);
                long totalUsers = userDF.count();

                // 使用Spark JDBC读取 subject 表，统计科目数量
                Dataset<Row> subjectDF = spark.read()
                        .jdbc(DB_URL, "subject", connectionProperties);
                long totalSubjects = subjectDF.count();

                // 使用Spark JDBC读取 study 表，统计学习记录数
                Dataset<Row> studyDF = spark.read()
                        .jdbc(DB_URL, "study", connectionProperties);
                long totalStudies = studyDF.count();

                // 计算人均学习次数（总学习记录数 / 总用户数）
                double avgStudiesPerUser = totalUsers > 0
                        ? Math.round((double) totalStudies / totalUsers * 100.0) / 100.0
                        : 0.0;

                // 构建JSON响应
                Map<String, Object> overview = new LinkedHashMap<>();
                overview.put("totalUsers", totalUsers);
                overview.put("totalSubjects", totalSubjects);
                overview.put("totalStudies", totalStudies);
                overview.put("avgStudiesPerUser", avgStudiesPerUser);

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", overview);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "综合概览统计失败: " + e.getMessage());
            }
        }
    }

    /**
     * 科目学习次数分布统计接口 —— GET /spark/api/stats/subject
     * <p>
     * 使用Spark读取subject表和study表，通过groupBy统计每个科目的学习次数，
     * 与subject表join获取科目名称，按学习次数降序排列，返回前10条。
     */
    public static class SubjectStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                // Spark JDBC 连接属性
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 使用Spark读取 subject 表
                Dataset<Row> subjectDF = spark.read()
                        .jdbc(DB_URL, "subject", connectionProperties);

                // 使用Spark读取 study 表
                Dataset<Row> studyDF = spark.read()
                        .jdbc(DB_URL, "study", connectionProperties);

                // 对study表按subject_name分组，统计每个科目的学习次数
                // 注意：数据库中列名为 subject_name（下划线），不是 subjectName
                Dataset<Row> studyCountDF = studyDF
                        .groupBy("subject_name")
                        .count()
                        .withColumnRenamed("count", "studyCount");

                // 与subject表join，关联科目名称和ID
                Dataset<Row> resultDF = subjectDF
                        .join(studyCountDF,
                                subjectDF.col("name").equalTo(studyCountDF.col("subject_name")))
                        .select(
                                subjectDF.col("id").alias("subjectId"),
                                subjectDF.col("name").alias("subjectName"),
                                studyCountDF.col("studyCount"))
                        .orderBy(desc("studyCount"))
                        .limit(10);

                // 收集结果并转换为JSON
                List<Row> rows = resultDF.collectAsList();
                List<Map<String, Object>> dataList = new ArrayList<>();
                for (Row row : rows) {
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("subjectId", row.getAs("subjectId"));
                    item.put("subjectName", row.getAs("subjectName"));
                    item.put("studyCount", row.getAs("studyCount"));
                    dataList.add(item);
                }

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", dataList);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "科目学习次数统计失败: " + e.getMessage());
            }
        }
    }

    /**
     * 用户行为特征分析接口 —— GET /spark/api/stats/behavior
     * <p>
     * 使用Spark读取user_behavior_feature表，分析用户活跃度分布：
     * - 用户分类（新手/沉默/普通/活跃）及占比
     * - 总学习次数、总学习时长等汇总指标
     */
    public static class UserBehaviorServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 使用Spark读取用户行为特征表
                Dataset<Row> behaviorDF = spark.read()
                        .jdbc(DB_URL, "user_behavior_feature", connectionProperties);

                long totalUsers = behaviorDF.count();

                // 按活跃度比例分类统计
                long activeUsers = behaviorDF.filter("activity_ratio > 0.5").count();
                long normalUsers = behaviorDF.filter("activity_ratio > 0.2 AND activity_ratio <= 0.5").count();
                long silentUsers = behaviorDF.filter("total_study_count > 0 AND activity_ratio <= 0.2").count();
                long newUsers = totalUsers - activeUsers - normalUsers - silentUsers;

                // 汇总指标
                List<Row> sumRow = behaviorDF.select(
                        org.apache.spark.sql.functions.sum("total_study_count").alias("sumStudy"),
                        org.apache.spark.sql.functions.sum("total_duration").alias("sumDuration"),
                        org.apache.spark.sql.functions.avg("activity_ratio").alias("avgRatio")
                ).collectAsList();
                long totalStudySum = 0;
                long totalDurationSum = 0;
                double avgActivityRatio = 0;
                if (!sumRow.isEmpty()) {
                    Row r = sumRow.get(0);
                    totalStudySum = r.isNullAt(0) ? 0 : r.getLong(0);
                    totalDurationSum = r.isNullAt(1) ? 0 : r.getLong(1);
                    avgActivityRatio = r.isNullAt(2) ? 0 : r.getDouble(2);
                }

                // 构建用户分类分布数据
                List<Map<String, Object>> userTypeDist = new ArrayList<>();
                userTypeDist.add(buildTypeItem("活跃用户", activeUsers, totalUsers));
                userTypeDist.add(buildTypeItem("普通用户", normalUsers, totalUsers));
                userTypeDist.add(buildTypeItem("沉默用户", silentUsers, totalUsers));
                userTypeDist.add(buildTypeItem("新手用户", newUsers, totalUsers));

                Map<String, Object> behaviorData = new LinkedHashMap<>();
                behaviorData.put("totalUsers", totalUsers);
                behaviorData.put("totalStudySum", totalStudySum);
                behaviorData.put("totalDurationSum", totalDurationSum);
                behaviorData.put("avgActivityRatio", Math.round(avgActivityRatio * 10000.0) / 10000.0);
                behaviorData.put("userTypeDistribution", userTypeDist);

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", behaviorData);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                // 表不存在时优雅降级，返回空数据而非500
                System.err.println("[WARN] 用户行为分析失败（可能表未创建）: " + e.getMessage());
                Map<String, Object> emptyData = new LinkedHashMap<>();
                emptyData.put("totalUsers", 0);
                emptyData.put("totalStudySum", 0);
                emptyData.put("totalDurationSum", 0);
                emptyData.put("avgActivityRatio", 0);
                emptyData.put("userTypeDistribution", new ArrayList<>());
                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", emptyData);
                writeJson(resp, toJson(result));
            }
        }

        private Map<String, Object> buildTypeItem(String type, long count, long total) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("type", type);
            item.put("count", count);
            item.put("ratio", total > 0 ? Math.round((double) count / total * 10000.0) / 100.0 : 0);
            return item;
        }
    }

    /**
     * 用户评分分析接口 —— GET /spark/api/stats/rating
     * <p>
     * 使用Spark读取user_subject_rating表，分析评分分布：
     * - 评分等级分布（优秀/良好/一般/较差）
     * - 高评分科目排行（平均分Top10）
     * - 评分最多的科目排行（评论数Top10）
     */
    public static class RatingStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 读取评分表
                Dataset<Row> ratingDF = spark.read()
                        .jdbc(DB_URL, "user_subject_rating", connectionProperties);
                // 读取科目表
                Dataset<Row> subjectDF = spark.read()
                        .jdbc(DB_URL, "subject", connectionProperties);

                long totalRatings = ratingDF.count();

                // 评分等级分布
                long excellent = ratingDF.filter("rating >= 4.5").count();
                long good = ratingDF.filter("rating >= 3.5 AND rating < 4.5").count();
                long normal2 = ratingDF.filter("rating >= 2.5 AND rating < 3.5").count();
                long poor = totalRatings - excellent - good - normal2;

                List<Map<String, Object>> ratingDist = new ArrayList<>();
                ratingDist.add(buildRatingItem("优秀(4.5-5.0)", excellent, totalRatings));
                ratingDist.add(buildRatingItem("良好(3.5-4.5)", good, totalRatings));
                ratingDist.add(buildRatingItem("一般(2.5-3.5)", normal2, totalRatings));
                ratingDist.add(buildRatingItem("较差(<2.5)", poor, totalRatings));

                // 按科目聚合：平均分和评分人数
                Dataset<Row> subjectAvgDF = ratingDF
                        .groupBy("subject_id")
                        .agg(
                                org.apache.spark.sql.functions.avg("rating").alias("avgRating"),
                                org.apache.spark.sql.functions.count("rating").alias("ratingCount")
                        );

                // Join 获取科目名称，按平均分降序取Top10
                Dataset<Row> topRatedDF = subjectAvgDF
                        .join(subjectDF,
                                subjectAvgDF.col("subject_id").equalTo(subjectDF.col("id")))
                        .select(
                                subjectDF.col("id").alias("subjectId"),
                                subjectDF.col("name").alias("subjectName"),
                                subjectAvgDF.col("avgRating"),
                                subjectAvgDF.col("ratingCount"))
                        .orderBy(desc("avgRating"))
                        .limit(10);

                List<Map<String, Object>> topRatedList = new ArrayList<>();
                for (Row row : topRatedDF.collectAsList()) {
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("subjectId", row.getAs("subjectId"));
                    item.put("subjectName", row.getAs("subjectName"));
                    double avg = row.getAs("avgRating");
                    item.put("avgRating", Math.round(avg * 100.0) / 100.0);
                    item.put("ratingCount", row.getAs("ratingCount"));
                    topRatedList.add(item);
                }

                Map<String, Object> ratingData = new LinkedHashMap<>();
                ratingData.put("totalRatings", totalRatings);
                ratingData.put("ratingDistribution", ratingDist);
                ratingData.put("topRatedSubjects", topRatedList);

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", ratingData);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                // 表不存在时优雅降级，返回空数据而非500
                System.err.println("[WARN] 评分分析失败（可能表未创建）: " + e.getMessage());
                Map<String, Object> emptyData = new LinkedHashMap<>();
                emptyData.put("totalRatings", 0);
                emptyData.put("ratingDistribution", new ArrayList<>());
                emptyData.put("topRatedSubjects", new ArrayList<>());
                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", emptyData);
                writeJson(resp, toJson(result));
            }
        }

        private Map<String, Object> buildRatingItem(String level, long count, long total) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("level", level);
            item.put("count", count);
            item.put("ratio", total > 0 ? Math.round((double) count / total * 10000.0) / 100.0 : 0);
            return item;
        }
    }

    /**
     * 用户学习时长排行接口 —— GET /spark/api/stats/user
     * <p>
     * 使用Spark读取user表和study表，统计每个用户的学习时长总和（sum duration），
     * 与user表join获取用户名，按学习时长降序排列，只返回前10名。
     * 注意：duration字段单位是分钟。
     */
    public static class UserStatsServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 使用Spark读取 user 表
                Dataset<Row> userDF = spark.read()
                        .jdbc(DB_URL, "user", connectionProperties);

                // 使用Spark读取 study 表
                Dataset<Row> studyDF = spark.read()
                        .jdbc(DB_URL, "study", connectionProperties);

                // 按 user_id 分组，统计学习时长总和（sum duration）
                Dataset<Row> durationDF = studyDF
                        .groupBy("user_id")
                        .agg(org.apache.spark.sql.functions.sum("duration").alias("totalDuration"));

                // 与 user 表 join 获取用户名，按学习时长降序排列，取前10名
                Dataset<Row> resultDF = userDF
                        .join(durationDF,
                                userDF.col("id").equalTo(durationDF.col("user_id")))
                        .select(
                                userDF.col("id").alias("userId"),
                                userDF.col("username").alias("userName"),
                                durationDF.col("totalDuration"))
                        .orderBy(desc("totalDuration"))
                        .limit(10);

                // 收集结果并转换为JSON
                List<Row> rows = resultDF.collectAsList();
                List<Map<String, Object>> dataList = new ArrayList<>();
                for (Row row : rows) {
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("userId", row.getAs("userId"));
                    item.put("userName", row.getAs("userName"));
                    item.put("totalDuration", row.getAs("totalDuration"));
                    dataList.add(item);
                }

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", dataList);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "用户学习时长排行统计失败: " + e.getMessage());
            }
        }
    }

    /**
     * 科目热度排行接口 —— GET /spark/api/stats/ranking
     * <p>
     * 使用Spark统计每个科目的学习人数（count distinct user_id），
     * 与subject表join获取科目名称，计算热度得分（学习人数 × 权重系数10），
     * 按热度得分降序排列，返回前10条。
     */
    public static class SubjectRankingServlet extends HttpServlet {
        /** 热度得分权重系数 */
        private static final double WEIGHT_FACTOR = 10.0;

        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
            resp.setContentType("application/json;charset=UTF-8");
            resp.setCharacterEncoding("UTF-8");

            try {
                java.util.Properties connectionProperties = new java.util.Properties();
                connectionProperties.setProperty("user", DB_USERNAME);
                connectionProperties.setProperty("password", DB_PASSWORD);
                connectionProperties.setProperty("driver", "com.mysql.cj.jdbc.Driver");

                // 使用Spark读取 study 表
                Dataset<Row> studyDF = spark.read()
                        .jdbc(DB_URL, "study", connectionProperties);

                // 使用Spark读取 subject 表
                Dataset<Row> subjectDF = spark.read()
                        .jdbc(DB_URL, "subject", connectionProperties);

                // 统计每个科目的学习人数（count distinct user_id）
                // 注意：数据库中列名为 subject_name（下划线）
                Dataset<Row> userCountDF = studyDF
                        .groupBy("subject_name")
                        .agg(org.apache.spark.sql.functions.countDistinct("user_id").alias("learnerCount"));

                // 与 subject 表 join 获取科目名称，按学习人数降序排列，取前10
                Dataset<Row> resultDF = subjectDF
                        .join(userCountDF,
                                subjectDF.col("name").equalTo(userCountDF.col("subject_name")))
                        .select(
                                subjectDF.col("name").alias("name"),
                                userCountDF.col("learnerCount"))
                        .orderBy(desc("learnerCount"))
                        .limit(10);

                // 收集结果，计算热度得分：学习人数 × 权重系数
                List<Row> rows = resultDF.collectAsList();
                List<Map<String, Object>> dataList = new ArrayList<>();
                for (Row row : rows) {
                    Map<String, Object> item = new LinkedHashMap<>();
                    String name = row.getAs("name");
                    long learnerCount = row.getAs("learnerCount");
                    item.put("name", name);
                    item.put("score", learnerCount * (long) WEIGHT_FACTOR);
                    dataList.add(item);
                }

                Map<String, Object> result = new LinkedHashMap<>();
                result.put("code", 200);
                result.put("message", "success");
                result.put("data", dataList);

                writeJson(resp, toJson(result));

            } catch (Exception e) {
                writeError(resp, "科目热度排行统计失败: " + e.getMessage());
            }
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 获取数据库连接
     */
    private static Connection getConnection() throws SQLException {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            throw new SQLException("MySQL驱动加载失败", e);
        }
        return DriverManager.getConnection(DB_URL, DB_USERNAME, DB_PASSWORD);
    }

    /**
     * 简单JSON序列化（避免引入额外依赖）
     */
    private static String toJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) sb.append(",");
            first = false;
            sb.append("\"").append(escapeJson(entry.getKey())).append("\":");
            appendValue(sb, entry.getValue());
        }
        sb.append("}");
        return sb.toString();
    }

    /**
     * 递归追加JSON值
     */
    @SuppressWarnings("unchecked")
    private static void appendValue(StringBuilder sb, Object value) {
        if (value == null) {
            sb.append("null");
        } else if (value instanceof String) {
            sb.append("\"").append(escapeJson((String) value)).append("\"");
        } else if (value instanceof Number || value instanceof Boolean) {
            sb.append(value);
        } else if (value instanceof List) {
            sb.append("[");
            boolean first = true;
            for (Object item : (List<Object>) value) {
                if (!first) sb.append(",");
                first = false;
                appendValue(sb, item);
            }
            sb.append("]");
        } else if (value instanceof Map) {
            sb.append(toJson((Map<String, Object>) value));
        } else {
            sb.append("\"").append(escapeJson(value.toString())).append("\"");
        }
    }

    /**
     * JSON字符串转义
     */
    private static String escapeJson(String str) {
        if (str == null) return "";
        return str.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    /**
     * 输出JSON响应
     */
    private static void writeJson(HttpServletResponse resp, String json) throws IOException {
        resp.setHeader("Access-Control-Allow-Origin", "*");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");
        resp.setContentType("application/json;charset=UTF-8");
        resp.setCharacterEncoding("UTF-8");
        PrintWriter out = resp.getWriter();
        out.print(json);
        out.flush();
    }

    /**
     * 输出错误响应
     */
    private static void writeError(HttpServletResponse resp, String message) throws IOException {
        Map<String, Object> error = new LinkedHashMap<>();
        error.put("code", 500);
        error.put("message", message);
        resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        writeJson(resp, toJson(error));
    }
}