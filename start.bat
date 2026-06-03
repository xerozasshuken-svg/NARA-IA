@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" --version >nul 2>nul
    if %ERRORLEVEL%==0 (
        "venv\Scripts\python.exe" run.py %*
        exit /b %ERRORLEVEL%
    )
)

echo No hay venv local usable. Ejecuta setup.bat o setup.ps1.
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 run.py %*
    exit /b %ERRORLEVEL%
)

python run.py %*
