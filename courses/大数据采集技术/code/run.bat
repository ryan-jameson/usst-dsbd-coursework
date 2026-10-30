@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 scraper_gui.py
) else (
    python scraper_gui.py
)

pause
