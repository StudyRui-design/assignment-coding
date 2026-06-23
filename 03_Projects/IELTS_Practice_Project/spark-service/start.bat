@echo off
chcp 65001 >nul
cd /d "%~dp0target"
echo ============================================
echo   启动 Spark 数据分析微服务（端口 9090）
echo ============================================
java -jar spark-service.jar
pause
