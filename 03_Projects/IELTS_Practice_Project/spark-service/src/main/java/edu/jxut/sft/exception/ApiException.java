package edu.jxut.sft.exception;

/**
 * Custom runtime exception carrying an HTTP status code.
 */
public class ApiException extends RuntimeException {

    private final int httpStatus;

    public ApiException(int httpStatus, String message) {
        super(message);
        this.httpStatus = httpStatus;
    }

    public ApiException(String message) {
        super(message);
        this.httpStatus = 500;
    }

    public ApiException(int httpStatus, String message, Throwable cause) {
        super(message, cause);
        this.httpStatus = httpStatus;
    }

    public ApiException(String message, Throwable cause) {
        super(message, cause);
        this.httpStatus = 500;
    }

    public int getHttpStatus() {
        return httpStatus;
    }
}