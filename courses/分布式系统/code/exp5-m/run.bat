@echo off
chcp 65001 >nul
echo ========================================================
echo    Java 现代内核浏览器 - 启动脚本 (实验五 - 改进版)
echo ========================================================
echo.

cd /d "%~dp0"

:: 检查是否已经下载了 JavaFX SDK 内核
set JFX_DIR=javafx-sdk\javafx-sdk-21.0.2\lib
if exist "%JFX_DIR%\javafx.web.jar" goto compile_start

echo [提示] 初次运行，需要下载真实的 WebKit 浏览器内核包...
echo [提示] 正在从 GluonHQ 下载 OpenJFX 21 (这可能需要几分钟，请耐心等待)
echo.

powershell -Command "try { Write-Host 'Downloading...'; Invoke-WebRequest -Uri 'https://download2.gluonhq.com/openjfx/21.0.2/openjfx-21.0.2_windows-x64_bin-sdk.zip' -OutFile 'jfx.zip'; Write-Host 'Download complete. Extracting...'; Expand-Archive -Path 'jfx.zip' -DestinationPath 'javafx-sdk' -Force; Remove-Item 'jfx.zip'; Write-Host 'Extraction complete!' } catch { Write-Host 'Error downloading JFX.'; exit 1 }"

if not exist "%JFX_DIR%\javafx.web.jar" (
    echo [错误] 内核包下载或解压失败！请检查你的网络连接。
    pause
    exit /b
)

:compile_start
echo [1/2] 正在编译现代浏览器核心代码...
if not exist "out" mkdir out

:: 拷贝样式文件和资源到 out 目录
copy /Y src\*.css out\ >nul

:: 使用引入的 SDK 进行编译
javac --module-path "%JFX_DIR%" --add-modules javafx.controls,javafx.web -encoding UTF-8 src/*.java -d out
if %ERRORLEVEL% neq 0 (
    echo [错误] 编译失败！
    pause
    exit /b
)

echo [2/2] 正在启动 现代化浏览器 GUI...
start "Modern Java Browser" java --module-path "%JFX_DIR%" --add-modules javafx.controls,javafx.web -cp "out" ModernBrowser

echo 浏览器成功拉起！感谢耐心等待。
exit
