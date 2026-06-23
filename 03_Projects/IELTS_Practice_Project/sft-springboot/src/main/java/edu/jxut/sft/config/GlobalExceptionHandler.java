package edu.jxut.sft.config;

import edu.jxut.sft.dto.ApiResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(Exception.class)
    public ApiResponse handleException(Exception e) {
        log.error("系统异常: {}", e.getMessage(), e);
        // 生产环境不暴露内部异常细节，仅返回通用错误信息
        return ApiResponse.error("服务器内部错误，请稍后重试");
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ApiResponse handleIllegalArgument(IllegalArgumentException e) {
        return ApiResponse.error(e.getMessage());
    }
}
