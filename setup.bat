@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set PYTHON_CMD=py -3
) else (
    where python >nul 2>nul
    if not %ERRORLEVEL%==0 (
        echo No se encontro Python. Instala Python 3.11 o superior.
        exit /b 1
    )
    set PYTHON_CMD=python
)

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" --version >nul 2>nul
    if not %ERRORLEVEL%==0 (
        echo El entorno virtual copiado no es usable en este equipo. Recreando venv...
        rmdir /s /q venv
    )
)

if not exist "venv" (
    %PYTHON_CMD% -m venv venv
)

"venv\Scripts\python.exe" -m pip install --upgrade pip
"venv\Scripts\python.exe" -m pip install -r requirements.txt

echo Entorno listo. Ejecuta: start.bat
