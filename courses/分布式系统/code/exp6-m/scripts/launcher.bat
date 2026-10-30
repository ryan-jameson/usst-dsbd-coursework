@echo off
setlocal enabledelayedexpansion
chcp 65001

set "ROOT=%~dp0.."
pushd "%ROOT%"

title 智能Web系统 - 实验6 启动器

:menu
echo ========================================
echo   智能Web服务器 - 实验6 启动器
Echo ========================================
echo   [1] 初始化环境 (数据库/依赖/日志)
echo   [2] 编译并启动服务器
echo   [3] 编译并启动客户端
echo   [4] 退出
echo ========================================
set /p choice=请选择操作 (1-4): 

if "%choice%"=="1" goto init
if "%choice%"=="2" goto start_server
if "%choice%"=="3" goto start_client
if "%choice%"=="4" goto end

echo 输入无效，请重试。
pause
goto menu

:init
echo ========================================
echo   智能Web服务器 - 实验6 初始化脚本
echo ========================================

echo [1/4] 检查Java环境...
java -version >nul 2>&1 || (echo Java未安装！ & pause & goto menu)

echo [2/4] 初始化数据库...
mysql -u root -p < database\init_schema.sql

echo [3/4] 检查依赖库...
if not exist "lib" mkdir lib
echo 请将以下JAR放入lib目录:
echo   - mysql-connector-java-8.x.jar
echo   - gson-2.x.jar
echo   - httpclient-4.x.jar

echo [4/4] 创建日志目录...
if not exist "logs" mkdir logs

echo ========================================
echo   初始化完成！
echo ========================================
pause
goto menu

:start_server
echo 正在编译服务器...
if not exist "out" mkdir out
set "SRC_LIST="
for /r "src\main\java" %%f in (*.java) do set "SRC_LIST=!SRC_LIST! %%f"
javac -encoding UTF-8 -d out !SRC_LIST!
if %errorlevel% neq 0 (
    echo 编译失败，请检查代码或依赖！
    pause
    goto menu
)

echo 正在启动服务器...
java -cp "out;src/main/resources;lib/*" com.experiment6.server.WebServer
pause
goto menu

:start_client
echo 正在编译客户端...
if not exist "out" mkdir out
set "SRC_LIST="
for /r "src\main\java" %%f in (*.java) do set "SRC_LIST=!SRC_LIST! %%f"
javac -encoding UTF-8 -d out !SRC_LIST!
if %errorlevel% neq 0 (
    echo 编译失败，请检查代码或依赖！
    pause
    goto menu
)

echo 正在启动客户端...
java -cp "out;src/main/resources;lib/*" com.experiment6.client.WebClient
pause
goto menu

:end
popd
endlocal
exit /b 0
