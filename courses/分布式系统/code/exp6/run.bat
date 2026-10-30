@echo off
chcp 65001 >nul
echo 正在编译 Web 服务器程序...
if not exist out mkdir out
javac -encoding UTF-8 -d out src\WebServer.java src\ClientHandler.java

if %errorlevel% neq 0 (
    echo Compile failed!
    pause
    exit /b %errorlevel%
)

echo Compile success!
echo Starting Web Server (Port: 8080)...
java -cp out WebServer
pause
