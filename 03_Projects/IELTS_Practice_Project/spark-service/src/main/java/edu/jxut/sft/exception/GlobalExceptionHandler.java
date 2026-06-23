package edu.jxut.sft.exception;

import com.alibaba.fastjson.JSON;
import edu.jxut.sft.model.ApiResponse;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Global exception handler — catches exceptions and returns unified JSON.
 */
public class GlobalExceptionHandler {

    /**
     * Write an exception as a JSON error response.
     */
    public static void handle(HttpServletResponse resp, Exception e) throws IOException {
        int status = 500;
        String message = "Internal server error";

        if (e instanceof ApiException) {
            ApiException ae = (ApiException) e;
            status = ae.getHttpStatus();
            message = ae.getMessage();
        } else {
            message = e.getMessage() != null ? e.getMessage() : message;
            e.printStackTrace(System.err);
        }

        resp.setStatus(status);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write(JSON.toJSONString(ApiResponse.error(status, message)));
    }

    /**
     * Write a success response as JSON.
     */
    public static void writeSuccess(HttpServletResponse resp, Object data) throws IOException {
        resp.setContentType("application/json;charset=UTF-8");
        resp.setStatus(HttpServletResponse.SC_OK);
        resp.getWriter().write(JSON.toJSONString(ApiResponse.success(data)));
    }
}
