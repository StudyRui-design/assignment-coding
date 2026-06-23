package edu.jxut.sft.controller;

import edu.jxut.sft.exception.GlobalExceptionHandler;
import edu.jxut.sft.service.RecommendationService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Machine Learning / Recommendation API endpoints: /api/ml/*
 *   - clusters              User behavior clustering
 *   - recommendations       Hot subject recommendations
 *   - hot-subjects          Hot subject list
 *   - user-recommendation   Personalized recommendation (?userId=N)
 */
public class MlController extends BaseServlet {

    private final RecommendationService recService = new RecommendationService();

    @Override
    protected void doHandle(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String path = req.getRequestURI();
        String action = path.substring(path.lastIndexOf('/') + 1);

        Object result;
        switch (action) {
            case "clusters":
                result = recService.userClusters();
                break;
            case "recommendations":
            case "hot-subjects":
                result = recService.defaultRecommendations();
                break;
            case "user-recommendation":
                int userId = 1;
                String uidStr = req.getParameter("userId");
                if (uidStr != null) {
                    try { userId = Integer.parseInt(uidStr); } catch (NumberFormatException ignored) {}
                }
                result = recService.personalizedRecommendations(userId);
                break;
            default:
                resp.sendError(HttpServletResponse.SC_NOT_FOUND, "Unknown ML endpoint: " + action);
                return;
        }

        GlobalExceptionHandler.writeSuccess(resp, result);
    }
}
