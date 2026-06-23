@echo off
chcp 65001 >nul
set "JAVA_HOME=D:\Dev\Java\jdk1.8.0_121"
set "MAVEN_HOME=D:\Dev\apache-maven-3.9.9"
set "Path=%MAVEN_HOME%\bin;%JAVA_HOME%\bin;%Path%"
echo ============================================
echo   编译 Spark 数据分析微服务
echo ============================================
cd /d "D:\Study\IELTS Parctice Project\spark-service"
call mvn clean package -DskipTests -q
IF ERRORLEVEL 1 (
    echo [ERROR] 编译失败！
    pause
    exit /b 1
)
echo.
echo ============================================
echo   启动 Spark 数据分析微服务（端口 9090）
echo ============================================
cd target
java -jar spark-service.jar
pause
