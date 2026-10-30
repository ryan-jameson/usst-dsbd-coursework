@echo off
echo 使用D盘Python环境运行图像处理脚本...
echo Python路径: D:\Python\python.exe
echo 脚本路径: %~dp0image_processing.py
echo.

D:\Python\python.exe "%~dp0image_processing.py"

echo.
echo 脚本执行完成！
pause
