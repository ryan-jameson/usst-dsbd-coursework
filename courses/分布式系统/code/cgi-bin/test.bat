@echo off
REM 输出当前时间作为简单 CGI 示例
for /f "tokens=1-2 delims==" %%a in ('wmic os get localdatetime /value ^| find "LocalDateTime"') do set t=%%b
set yyyy=%t:~0,4%
set mm=%t:~4,2%
set dd=%t:~6,2%
set hh=%t:~8,2%
set mi=%t:~10,2%
set ss=%t:~12,2%
echo 当前时间: %yyyy%-%mm%-%dd% %hh%:%mi%:%ss%
