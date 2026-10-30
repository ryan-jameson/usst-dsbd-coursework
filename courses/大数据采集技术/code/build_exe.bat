@echo off
cd /d "%~dp0"

echo Installing PyInstaller if needed...
py -3 -m pip install --upgrade pyinstaller

echo Building Windows executable...
py -3 -m PyInstaller --onefile --windowed --name WebScraperGUI scraper_gui.py

echo.
echo Build finished. The executable is:
echo dist\WebScraperGUI.exe
echo.
pause
