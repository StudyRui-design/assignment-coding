@echo off
chcp 65001 >nul
echo ============================================
echo   Recruitment Role Data Analytics
echo ============================================
echo.

cd /d "%~dp0"

REM Step 1: 数据库初始化
echo [1/6] 检查MySQL连接...
python -c "import pymysql; pymysql.connect(host='localhost',user='root',password='123456',db='recruitment_db',charset='utf8mb4'); print('OK - MySQL连接成功')"
if errorlevel 1 (
    echo [ERROR] MySQL连接失败，请检查数据库服务是否启动
    pause
    exit /b 1
)

REM Step 2: 安装 Playwright 浏览器（若未安装）
echo.
echo [2/6] 检查 Playwright Chromium...
python -c "from playwright.sync_api import sync_playwright; pw = sync_playwright().start(); pw.chromium.launch(headless=True); pw.stop(); print('OK - Chromium就绪')"
if errorlevel 1 (
    echo [WARN] Playwright Chromium 未安装，尝试安装...
    python -m playwright install chromium
)

REM Step 3: 数据扩充入库
echo.
echo [3/6] 数据扩充入库...
python data_expansion.py
if errorlevel 1 (
    echo [WARN] 数据扩充有错误，尝试继续...
)

REM Step 4: 数据分析可视化
echo.
echo [4/6] 数据分析可视化（生成8张图表）...
python data_analysis.py
if errorlevel 1 (
    echo [WARN] 数据分析有错误，尝试继续...
)

REM Step 5: 机器学习建模
echo.
echo [5/6] 机器学习模型训练...
python ml_models.py
if errorlevel 1 (
    echo [WARN] 模型训练有错误，尝试继续...
)

REM Step 6: 复制模型和图片到Web项目
echo.
echo [6/6] 部署Web平台文件...
if not exist "recruitment_project\models" mkdir "recruitment_project\models"
xcopy /Y "models\*.pkl" "recruitment_project\models\" >nul
if not exist "recruitment_project\static\images" mkdir "recruitment_project\static\images"
xcopy /Y "static\images\*.png" "recruitment_project\static\images\" >nul

echo.
echo ============================================
echo   启动 Flask Web 平台 (端口5000)
echo   地址: http://127.0.0.1:5000
echo ============================================
cd recruitment_project
python app.py

pause
