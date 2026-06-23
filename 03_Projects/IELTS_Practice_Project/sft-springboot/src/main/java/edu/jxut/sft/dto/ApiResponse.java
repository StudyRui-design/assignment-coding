package edu.jxut.sft.dto;

import java.util.HashMap;
import java.util.Map;

public class ApiResponse {

    private int code;
    private String message;
    private Object data;

    public ApiResponse() {}

    public ApiResponse(int code, String message, Object data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    public static ApiResponse success() {
        return new ApiResponse(200, "操作成功", null);
    }

    public static ApiResponse success(Object data) {
        return new ApiResponse(200, "操作成功", data);
    }

    public static ApiResponse success(String message, Object data) {
        return new ApiResponse(200, message, data);
    }

    public static ApiResponse success(int code, String message, Object data) {
        return new ApiResponse(code, message, data);
    }

    public static ApiResponse error(String message) {
        return new ApiResponse(500, message, null);
    }

    public static ApiResponse error(int code, String message) {
        return new ApiResponse(code, message, null);
    }

    public static ApiResponse unauthorized() {
        return new ApiResponse(401, "未登录或登录已过期", null);
    }

    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public Object getData() { return data; }
    public void setData(Object data) { this.data = data; }

    /**
     * 快捷构建分页数据
     */
    public static Map<String, Object> pageData(Object list, long total, int page, int pageSize) {
        Map<String, Object> map = new HashMap<>();
        map.put("list", list);
        map.put("total", total);
        map.put("page", page);
        map.put("pageSize", pageSize);
        return map;
    }
}
