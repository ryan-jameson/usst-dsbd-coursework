@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "%SCRIPT_DIR%football_gui.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%SCRIPT_DIR%football_gui.py"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" python "%SCRIPT_DIR%football_gui.py"
    exit /b 0
)

echo Python was not found. Please install Python 3 and try again.
pause
exit /b 1
