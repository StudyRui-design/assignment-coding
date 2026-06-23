package edu.jxut.sft;

import edu.jxut.sft.config.AppConfig;
import edu.jxut.sft.config.SparkConfig;
import edu.jxut.sft.controller.MlController;
import edu.jxut.sft.controller.OpenApiServlet;
import edu.jxut.sft.controller.StatsController;
import edu.jxut.sft.streaming.LearningStreamApp;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.DefaultServlet;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

import java.net.URL;

/**
 * ============================================
 *  大数据技术开发实训 — Spark 数据分析微服务
 * ============================================
 *
 * 重构版本: Controller / Service / DAO 三层架构
 * 新增:     全局异常处理 + Swagger UI + Spark Streaming
 *
 * 启动方式:
 *   A) mvn clean package exec:java
 *   B) java -jar target/spark-service.jar
 *
 * 访问地址:
 *   API:       http://localhost:9090/api/*
 *   Swagger:   http://localhost:9090/swagger
 *   OpenAPI:   http://localhost:9090/api/openapi.json
 */
public class SparkServerApplication {

    public static void main(String[] args) throws Exception {
        printBanner();

        // 1. Initialize Spark
        SparkConfig.getSparkSession();

        // --- Optional: start real-time streaming ---
        // Uncomment the line below to enable structured streaming:
        // LearningStreamApp.start();
        // (For production, configure Kafka source in LearningStreamApp.java)

        // 2. Start Jetty server
        startJetty();
    }

    private static void startJetty() throws Exception {
        Server server = new Server(AppConfig.PORT);
        ServletContextHandler ctx = new ServletContextHandler(ServletContextHandler.SESSIONS);
        ctx.setContextPath(AppConfig.CONTEXT_PATH);
        server.setHandler(ctx);

        // ===== Stats API =====
        ctx.addServlet(new ServletHolder(new StatsController()), "/api/stats/*");

        // ===== ML / Recommend API =====
        ctx.addServlet(new ServletHolder(new MlController()), "/api/ml/*");

        // ===== OpenAPI spec =====
        ctx.addServlet(new ServletHolder(new OpenApiServlet()), "/api/openapi.json");
        ctx.addServlet(new ServletHolder(new OpenApiServlet()), "/api/openapi");

        // ===== Swagger UI static files =====
        URL swaggerRes = SparkServerApplication.class.getResource("/swagger");
        if (swaggerRes != null) {
            ServletHolder swaggerHolder = new ServletHolder("swagger-default", DefaultServlet.class);
            swaggerHolder.setInitParameter("resourceBase", swaggerRes.toExternalForm());
            swaggerHolder.setInitParameter("dirAllowed", "false");
            ctx.addServlet(swaggerHolder, "/swagger/*");
            System.out.println("  Swagger UI: /swagger");
        } else {
            System.out.println("  ⚠ Swagger UI static files not found, skipping.");
        }

        server.start();

        System.out.println("\n=========================================");
        System.out.println("  🚀 Spark 数据分析微服务启动成功！");
        System.out.println("  监听端口: http://localhost:" + AppConfig.PORT);
        System.out.println("=========================================\n");
        System.out.println("  📡 可用接口列表:");
        System.out.println("  ├── GET /api/stats/overview        系统综合概览");
        System.out.println("  ├── GET /api/stats/subject         科目学习分布");
        System.out.println("  ├── GET /api/stats/user?limit=N    用户学习排行");
        System.out.println("  ├── GET /api/stats/ranking         科目热度排行");
        System.out.println("  ├── GET /api/ml/clusters           用户聚类分析");
        System.out.println("  ├── GET /api/ml/recommendations    热门推荐");
        System.out.println("  ├── GET /api/ml/hot-subjects       热门科目列表");
        System.out.println("  ├── GET /api/ml/user-recommendation?userId=N  个性化推荐");
        System.out.println("  ├── GET /api/openapi.json          OpenAPI 规范");
        System.out.println("  └── /swagger                        Swagger UI（交互式文档）\n");

        server.join();
    }

    private static void printBanner() {
        System.out.println("\n" +
                "  ╔═══════════════════════════════════════════════╗\n" +
                "  ║   📊 大数据技术开发实训 — Spark 数据分析微服务 ║\n" +
                "  ║   Refactored: Controller / Service / DAO     ║\n" +
                "  ╚═══════════════════════════════════════════════╝\n");
    }
}
