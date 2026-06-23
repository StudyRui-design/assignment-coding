# ============================================
# 邓睿的大数据应用课件管理系统 - Docker 部署配置
# ============================================

# 第一阶段：构建
FROM maven:3.8-openjdk-8 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# 第二阶段：运行
FROM openjdk:8-jre-alpine
WORKDIR /app

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

COPY --from=builder /app/target/sft.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
