@echo off
chcp 65001 >nul
echo 正在编译 AI 客户端与 Web 服务端...
if not exist out mkdir out

:: 将 MySQL 驱动加入 classpath 进行编译
javac -encoding UTF-8 -cp "..\exp4\lib\mysql-connector-java-8.0.22.jar" -d out src\WebServer.java src\ClientHandler.java src\WebServerGUI.java src\WebClientGUI.java

if %errorlevel% neq 0 (
    echo Compile failed!
    pause
    exit /b %errorlevel%
)

echo 编译成功！
echo [1] 启动 Web 服务端监控台 (带 AI 拓展思路)
echo [2] 启动 AI Web 客户端 (可视化界面，结合了 MySQL)
echo.
set /p choice="请选择你要启动的应用 (1/2): "

if "%choice%"=="1" (
    java -cp out WebServerGUI
) else if "%choice%"=="2" (
    :: 运行时同样需要 MySQL 的驱动以提供 JDBC 链接
    java -cp "out;..\exp4\lib\mysql-connector-java-8.0.22.jar" WebClientGUI
) else (
    echo 输入无效, 退出。
)
pause
