package edu.jxut.sft;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletComponentScan;

/**
 * Spring Boot 主启动类
 */
@SpringBootApplication
@ServletComponentScan(basePackages = "edu.jxut.sft.servlets")
public class SftApplication {

    public static void main(String[] args) {
        SpringApplication.run(SftApplication.class, args);
        System.out.println("========================================");
        System.out.println("  邓睿的大数据应用课件管理系统 启动成功！");
        System.out.println("  访问地址: http://localhost:8080");
        System.out.println("========================================");
    }
}
