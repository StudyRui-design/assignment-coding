package edu.jxut.sft;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SftApplication {
    public static void main(String[] args) {
        SpringApplication.run(SftApplication.class, args);
        System.out.println("\n==========================================");
        System.out.println("  SFT Spring Boot 后端启动成功!");
        System.out.println("  访问地址: http://localhost:8080");
        System.out.println("==========================================\n");
    }
}
