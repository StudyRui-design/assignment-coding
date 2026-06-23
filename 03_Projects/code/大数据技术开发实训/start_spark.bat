@echo off
cd /d "d:\Study\code\大数据技术开发实训"
echo === Spark微服务启动中 (端口9090) ===
echo.

set "CP=target\classes"
for %%f in ("BOOT-INF\lib\*.jar") do set "CP=%CP%;BOOT-INF\lib\%%~nxf"

echo Starting SparkServer...
echo.
java -cp "%CP%" edu.jxut.sft.SparkServer

echo.
echo SparkServer exited with code %ERRORLEVEL%
pause
