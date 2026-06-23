@echo off
curl -s -X POST "http://localhost:8080/sft/login" -d "username=admin&password=123456"
echo.
echo --- Follow redirect ---
curl -s -L -c cookies.txt -b cookies.txt -X POST "http://localhost:8080/sft/login" -d "username=admin&password=123456" -o nul -w "HTTP_CODE: %%{http_code}\nURL: %%{redirect_url}"
echo.
echo --- Access index ---
curl -s -b cookies.txt "http://localhost:8080/sft/index.html" -o nul -w "HTTP_CODE: %%{http_code}\nREDIRECT_URL: %%{redirect_url}"
