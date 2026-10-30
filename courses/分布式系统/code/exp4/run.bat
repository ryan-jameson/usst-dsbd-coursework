@echo off
chcp 65001 >nul
echo =======================================
echo    RMI 分布式系统 (实验四) 启动脚本
echo =======================================

cd /d "%~dp0"

echo [1/4] 正在检查依赖目录 (lib)...
if not exist "lib" mkdir lib

echo [2/4] 正在编译所有的 Java 源代码...
if not exist "out" mkdir out
javac -encoding UTF-8 -cp "lib/*" src/*.java -d out
if %ERRORLEVEL% neq 0 (
    echo 编译失败，请检查代码或确认是否缺少必要环境。
    pause
    exit /b
)

echo [3/4] 正在启动 RMI 服务端图形界面...
:: 使用 start 命令新开一个独立窗口运行服务端，并与当前窗口解绑
start "RMI Server" java -cp "out;lib/*" RMIServer

echo [等待2秒，确保服务端已完全启动并绑定端口...]
timeout /t 2 >nul

echo [4/4] 正在启动 RMI 客户端图形界面...
:: 同样新开一个独立窗口运行客户端
start "RMI Client" java -cp "out;lib/*" RMIClient

echo 启动成功！你可以关闭当前控制台窗口了。
exit
