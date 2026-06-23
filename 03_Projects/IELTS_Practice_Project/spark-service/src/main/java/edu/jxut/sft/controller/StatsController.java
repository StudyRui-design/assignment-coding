package edu.jxut.sft.controller;

import com.alibaba.fastjson.JSON;
import edu.jxut.sft.exception.GlobalExceptionHandler;
import edu.jxut.sft.service.StatsService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Statistics API endpoints: /api/stats/*
 *   - overview      System overview
 *   - subject       Subject study distribution
 *   - user          Top study users
 *   - ranking       Subject popularity ranking
 *   - rating-dist   Rating score distribution
 */
public class StatsController extends BaseServlet {

    private final StatsService statsService = new StatsService();

    @Override
    protected void doHandle(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String path = req.getRequestURI();
        String action = path.substring(path.lastIndexOf('/') + 1);

        Object result;
        switch (action) {
            case "overview":
                result = statsService.overview();
                break;
            case "subject":
                result = statsService.subjectDistribution();
                break;
            case "user":
                int limit = 10;
                String limitStr = req.getParameter("limit");
                if (limitStr != null) {
                    try { limit = Integer.parseInt(limitStr); } catch (NumberFormatException ignored) {}
                }
                result = statsService.topUsers(limit);
                break;
            case "ranking":
                result = statsService.subjectRanking();
                break;
            default:
                resp.sendError(HttpServletResponse.SC_NOT_FOUND, "Unknown stats endpoint: " + action);
                return;
        }

        GlobalExceptionHandler.writeSuccess(resp, result);
    }
}
