@echo off
setlocal enabledelayedexpansion
chcp 65001
title 智能Web客户端 - 实验6
set "ROOT=%~dp0.."
pushd "%ROOT%"

echo 正在编译客户端...
if not exist "out" mkdir out
set "SRC_LIST="
for /r "src\main\java" %%f in (*.java) do set "SRC_LIST=!SRC_LIST! %%f"
javac -encoding UTF-8 -d out !SRC_LIST!
if %errorlevel% neq 0 (
	echo 编译失败，请检查代码或依赖！
	pause
	exit /b %errorlevel%
)

echo 正在启动客户端...
java -cp "out;src/main/resources;lib/*" com.experiment6.client.WebClient
popd
pause
