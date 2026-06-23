@echo off
chcp 65001 >nul
set "JAVA_HOME=D:\Dev\Java\jdk1.8.0_121"
set "MAVEN_HOME=D:\Dev\apache-maven-3.9.9"
set "Path=%MAVEN_HOME%\bin;%JAVA_HOME%\bin;%Path%"
cd /d "D:\Study\IELTS Parctice Project\spark-service"
echo ============================================
echo   编译 Spark 数据分析微服务
echo ============================================
call mvn clean package -DskipTests -q
echo BUILD_EXIT_CODE=%ERRORLEVEL%
pause
