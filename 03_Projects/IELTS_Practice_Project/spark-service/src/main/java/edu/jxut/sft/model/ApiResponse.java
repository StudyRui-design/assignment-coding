package edu.jxut.sft.model;

import com.alibaba.fastjson.JSONObject;

/**
 * Unified JSON API response wrapper.
 */
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

    public static ApiResponse success(Object data) {
        return new ApiResponse(200, "ok", data);
    }

    public static ApiResponse success() {
        return new ApiResponse(200, "ok", null);
    }

    public static ApiResponse error(int code, String message) {
        return new ApiResponse(code, message, null);
    }

    public static ApiResponse error(String message) {
        return new ApiResponse(500, message, null);
    }

    /** Convenient: wrap into a FastJSON JSONObject ready to write */
    public JSONObject toJSON() {
        JSONObject obj = new JSONObject(true);
        obj.put("code", code);
        obj.put("message", message);
        obj.put("data", data);
        return obj;
    }

    // Getters / Setters
    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public Object getData() { return data; }
    public void setData(Object data) { this.data = data; }
}
