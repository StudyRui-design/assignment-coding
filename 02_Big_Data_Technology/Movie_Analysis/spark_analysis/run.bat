@echo off
REM ================================================================
REM  Spark 电影分析 — Windows 提交脚本
REM
REM  用法:
REM    .\run.bat                   运行全部（含 MySQL + HDFS）
REM    .\run.bat --skip-mysql      跳过 MySQL
REM    .\run.bat --skip-hdfs       跳过 HDFS
REM
REM  前置条件:
REM    1. SPARK_HOME 环境变量已设置
REM    2. MySQL JDBC jar 已在 Spark jars 目录中
REM ================================================================

setlocal enabledelayedexpansion

REM 项目路径
set PROJ_DIR=%~dp0
set MAIN_PY=%PROJ_DIR%main.py

REM Spark 配置
set SPARK_MASTER=local[*]
set DRIVER_MEMORY=2g
set EXECUTOR_MEMORY=2g

REM MySQL JDBC jar 路径（按实际情况调整）
set MYSQL_JAR=%SPARK_HOME%\jars\mysql-connector-java-8.0.33.jar

if not exist "%MYSQL_JAR%" (
    echo [警告] 找不到 MySQL JDBC jar: %MYSQL_JAR%
    echo         请将 mysql-connector-java-8.0.33.jar 放入 %SPARK_HOME%\jars\
)

echo ================================================================
echo   Spark SQL MovieLens 1M Analysis
echo ================================================================
echo   Master : %SPARK_MASTER%
echo   Driver : %DRIVER_MEMORY%
echo ================================================================

spark-submit ^
    --master %SPARK_MASTER% ^
    --driver-memory %DRIVER_MEMORY% ^
    --executor-memory %EXECUTOR_MEMORY% ^
    --jars "%MYSQL_JAR%" ^
    "%MAIN_PY%" ^
    %*

echo.
echo 完成。按任意键退出...
pause >nul
