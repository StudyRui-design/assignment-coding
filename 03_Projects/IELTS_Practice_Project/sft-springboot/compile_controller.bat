@echo off
setlocal
set "JAVA_HOME=D:\Dev\Java\jdk1.8.0_121"
set "BASE=D:\Study\IELTS Parctice Project\sft-springboot"
set "M2=C:\Users\26291\.m2\repository"

:: Build classpath
set "CP=%BASE%\target\classes"
for %%I in (
  "%M2%\org\springframework\spring-webmvc\5.3.31\spring-webmvc-5.3.31.jar"
  "%M2%\org\springframework\spring-web\5.3.31\spring-web-5.3.31.jar"
  "%M2%\org\springframework\spring-beans\5.3.31\spring-beans-5.3.31.jar"
  "%M2%\org\springframework\spring-context\5.3.31\spring-context-5.3.31.jar"
  "%M2%\org\springframework\spring-core\5.3.31\spring-core-5.3.31.jar"
  "%M2%\org\springframework\spring-jdbc\5.3.31\spring-jdbc-5.3.31.jar"
  "%M2%\org\springframework\spring-tx\5.3.31\spring-tx-5.3.31.jar"
  "%M2%\org\springframework\spring-aop\5.3.31\spring-aop-5.3.31.jar"
) do set "CP=!CP!;%%~I"

echo Compiling DashboardController...
"%JAVA_HOME%\bin\javac.exe" -encoding UTF-8 -d "%BASE%\target\classes" -cp "%CP%" "%BASE%\src\main\java\edu\jxut\sft\controller\DashboardController.java"

if %ERRORLEVEL%==0 (
  echo [OK] Compiled successfully
) else (
  echo [FAIL] Compilation error
)

endlocal
