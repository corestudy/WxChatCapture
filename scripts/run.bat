@echo off
chcp 65001 >nul

REM Smart Screenshot Tool - Unified Windows launcher
REM Usage:
REM   run.bat install   - Install core dependencies from requirements.txt
REM   run.bat run       - Start main GUI
REM   run.bat simple    - Launch simple visual test tool
REM   run.bat debug     - Run debug runner with detailed checks
REM   run.bat check     - Check imports and environment
REM   run.bat extras    - (Optional) Install extra free libraries for compliance/reporting
REM   run.bat help      - Show help menu

setlocal ENABLEDELAYEDEXPANSION

if "%~1"=="" goto :menu
if /I "%~1"=="help" goto :help
if /I "%~1"=="install" goto :install
if /I "%~1"=="run" goto :run
if /I "%~1"=="simple" goto :simple
if /I "%~1"=="debug" goto :debug
if /I "%~1"=="check" goto :check
if /I "%~1"=="extras" goto :extras

echo ❌ Unknown command: %~1
goto :help

:menu
cls
echo ==================================================
echo 🚀 Smart Screenshot Tool - Unified Launcher
echo ==================================================
echo Current directory: %CD%

:help
echo.
echo Commands:
echo   install   Install dependencies (pip install -r requirements.txt)
echo   run       Start main GUI (python src\main.py)
echo   simple    Run simple test GUI (python tools\simple_test.py)
echo   debug     Run debug checks (python tools\debug_run.py)
echo   check     Check imports (python tools\check_imports.py)
echo   extras    Install optional extras (cryptography, requests, fpdf2, psutil)

echo.
if "%~1"=="help" goto :eof
if "%~1"=="" (
    set /p choice=Enter command [install/run/simple/debug/check/extras]: 
    if "%choice%"=="" goto :eof
    call "%~f0" %choice%
    goto :eof
)

echo.
echo 🔍 Checking Python...
python --version >nul 2>nul
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+
    goto :eof
)

goto :%~1

:install
echo.
echo 📦 Installing dependencies from requirements.txt ...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Dependency installation failed.
) else (
    echo ✅ Dependencies installed successfully.
)
goto :eof

:run
if not exist "src\main.py" (
    echo ❌ src\main.py not found. Please run from project root.
    goto :eof
)
python src\main.py
if errorlevel 1 (
    echo ❌ Program exited with errors.
)
goto :eof

:simple
python tools\simple_test.py
if errorlevel 1 (
    echo ❌ Simple test failed.
)
goto :eof

:debug
python tools\debug_run.py
if errorlevel 1 (
    echo ❌ Debug run reported issues.
)
goto :eof

:check
python tools\check_imports.py
if errorlevel 1 (
    echo ❌ Import check failed.
)
goto :eof

:extras
echo.
echo 📦 Installing optional, free extras for compliance/reporting ...
python -m pip install "cryptography>=3.4.8" "requests>=2.25.1" "fpdf2>=2.5.0" "psutil>=5.8.0"
if errorlevel 1 (
    echo ⚠️  Some optional extras failed to install.
) else (
    echo ✅ Optional extras installed successfully.
)
goto :eof

:end
endlocal
exit /b 0
