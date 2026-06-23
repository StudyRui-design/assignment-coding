package edu.jxut.sft.controller;

import edu.jxut.sft.exception.GlobalExceptionHandler;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Base servlet with CORS headers and centralized error handling.
 */
public abstract class BaseServlet extends HttpServlet {

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        // CORS headers
        resp.setHeader("Access-Control-Allow-Origin", "*");
        resp.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
        resp.setHeader("Access-Control-Max-Age", "86400");

        // Handle preflight
        if ("OPTIONS".equalsIgnoreCase(req.getMethod())) {
            resp.setStatus(HttpServletResponse.SC_OK);
            return;
        }

        try {
            doHandle(req, resp);
        } catch (Exception e) {
            GlobalExceptionHandler.handle(resp, e);
        }
    }

    /**
     * Subclasses implement this instead of doGet/doPost directly,
     * and enjoy automatic CORS + error handling.
     */
    protected abstract void doHandle(HttpServletRequest req, HttpServletResponse resp) throws Exception;
}
