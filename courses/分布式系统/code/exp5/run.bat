@echo off
chcp 65001 >nul
echo =======================================
echo    HTTP 简易浏览器 (实验五) 启动脚本
echo =======================================

cd /d "%~dp0"

echo [1/2] 正在编译所有的 Java 源代码...
if not exist "out" mkdir out
javac -encoding UTF-8 src/*.java -d out
if %ERRORLEVEL% neq 0 (
    echo 编译失败，请检查代码。
    pause
    exit /b
)

echo [2/2] 正在启动 美化版浏览器 GUI...
start "Simple Browser" java -cp "out" SimpleBrowserGUI

echo 启动成功！你可以关闭当前控制台窗口了。
exit
