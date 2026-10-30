@echo off
REM 简单 CGI 示例，输出 HTML 与时间
setlocal enabledelayedexpansion

echo ^<h1^>CGI Script Executed^</h1^>
echo ^<p^>Hello from CGI^</p^>
echo ^<p^>Current Time: %time%^</p^>
