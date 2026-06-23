package edu.jxut.sft.controller;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import edu.jxut.sft.exception.GlobalExceptionHandler;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Serves OpenAPI 3.0 specification at /api/openapi.json
 * Used by Swagger UI for interactive API documentation.
 */
public class OpenApiServlet extends BaseServlet {

    @Override
    protected void doHandle(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        JSONObject spec = new JSONObject(true);

        spec.put("openapi", "3.0.3");
        JSONObject info = new JSONObject(true);
        info.put("title", "Spark 数据分析微服务 API");
        info.put("description", "大数据技术开发实训 · Spark 数据分析与机器学习推荐微服务\n\n" +
                "提供统计数据查询、学习行为分析和个性化推荐功能。");
        info.put("version", "1.0.0");
        spec.put("info", info);

        JSONObject servers = new JSONObject(true);
        servers.put("url", "http://localhost:9090");
        servers.put("description", "Spark 微服务本地服务");
        spec.put("servers", new JSONArray() {{ add(servers); }});

        // ===== Paths =====
        JSONObject paths = new JSONObject(true);

        // GET /api/stats/overview
        JSONObject overviewPath = buildGetPath(
                "系统综合概览",
                "获取用户数、科目数、学习记录数、评分记录数等系统核心指标",
                "统计数据",
                new JSONObject(true) {{
                    put("200", buildResponse("成功返回系统概览",
                            new JSONObject(true) {{
                                put("type", "object");
                                put("properties", new JSONObject(true) {{
                                    put("userCount", new JSONObject(true) {{ put("type", "integer"); put("description", "用户总数"); }});
                                    put("subjectCount", new JSONObject(true) {{ put("type", "integer"); put("description", "科目总数"); }});
                                    put("studyCount", new JSONObject(true) {{ put("type", "integer"); put("description", "学习记录数"); }});
                                    put("ratingCount", new JSONObject(true) {{ put("type", "integer"); put("description", "评分记录数"); }});
                                }});
                            }}
                    ));
                }}
        );
        paths.put("/api/stats/overview", overviewPath);

        // GET /api/stats/subject
        paths.put("/api/stats/subject", buildGetPath(
                "科目学习分布",
                "获取各科目的学习人数和学习记录数分布",
                "统计数据"
        ));

        // GET /api/stats/user?limit=10
        JSONObject userPath = buildGetPath(
                "用户学习时长排行",
                "获取学习时长 TOP N 用户",
                "统计数据",
                new JSONObject(true) {{
                    put("parameters", new JSONArray() {{
                        add(new JSONObject(true) {{
                            put("name", "limit");
                            put("in", "query");
                            put("description", "返回条数（默认 10）");
                            put("schema", new JSONObject(true) {{ put("type", "integer"); }});
                        }});
                    }});
                }}
        );
        paths.put("/api/stats/user", userPath);

        // GET /api/stats/ranking
        paths.put("/api/stats/ranking", buildGetPath(
                "科目热度排行",
                "按平均评分和学习人数对科目进行排名",
                "统计数据"
        ));

        // GET /api/ml/clusters
        paths.put("/api/ml/clusters", buildGetPath(
                "用户行为聚类分析",
                "基于评分数据的用户活跃度聚类（高活跃/中等活跃/低活跃）",
                "机器学习"
        ));

        // GET /api/ml/recommendations
        paths.put("/api/ml/recommendations", buildGetPath(
                "热门科目推荐",
                "获取平均评分 >= 4.0 的热门科目推荐列表",
                "机器学习"
        ));

        // GET /api/ml/hot-subjects
        paths.put("/api/ml/hot-subjects", buildGetPath(
                "热门科目列表",
                "热门科目列表（同 /api/ml/recommendations）",
                "机器学习"
        ));

        // GET /api/ml/user-recommendation?userId=N
        JSONObject userRecPath = buildGetPath(
                "个性化科目推荐",
                "根据用户已学内容排除已学科目，推荐高分未学科目",
                "机器学习",
                new JSONObject(true) {{
                    put("parameters", new JSONArray() {{
                        add(new JSONObject(true) {{
                            put("name", "userId");
                            put("in", "query");
                            put("description", "用户 ID（默认 1）");
                            put("required", false);
                            put("schema", new JSONObject(true) {{ put("type", "integer"); }});
                        }});
                    }});
                }}
        );
        paths.put("/api/ml/user-recommendation", userRecPath);

        spec.put("paths", paths);

        GlobalExceptionHandler.writeSuccess(resp, spec);
    }

    private JSONObject buildGetPath(String summary, String description, String tag) {
        return buildGetPath(summary, description, tag, null);
    }

    private JSONObject buildGetPath(String summary, String description, String tag, JSONObject extra) {
        JSONObject path = new JSONObject(true);
        JSONObject get = new JSONObject(true);
        get.put("summary", summary);
        get.put("description", description);
        get.put("tags", new JSONArray() {{ add(tag); }});
        get.put("responses", new JSONObject(true) {{
            put("200", buildResponse("成功", null));
            put("500", buildResponse("服务器内部错误", null));
        }});

        if (extra != null && extra.containsKey("parameters")) {
            get.put("parameters", extra.getJSONArray("parameters"));
        }

        path.put("get", get);
        return path;
    }

    private JSONObject buildResponse(String description, JSONObject schema) {
        JSONObject resp = new JSONObject(true);
        resp.put("description", description);
        if (schema != null) {
            resp.put("content", new JSONObject(true) {{
                put("application/json", new JSONObject(true) {{
                    put("schema", schema);
                }});
            }});
        }
        return resp;
    }
}
