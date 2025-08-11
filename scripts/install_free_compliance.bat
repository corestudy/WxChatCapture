@echo off
chcp 65001 >nul
echo ================================================
echo Free Legal Compliance System Installer
echo All libraries are completely FREE and open source
echo ================================================

echo.
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo.
echo Installing free cryptographic library...
python -m pip install cryptography>=3.4.8
if errorlevel 1 (
    echo WARNING: cryptography installation failed
) else (
    echo SUCCESS: cryptography installed
)

echo.
echo Installing free HTTP library...
python -m pip install requests>=2.25.1
if errorlevel 1 (
    echo WARNING: requests installation failed
) else (
    echo SUCCESS: requests installed
)

echo.
echo Installing free PDF library (optional)...
python -m pip install fpdf2>=2.5.0
if errorlevel 1 (
    echo WARNING: fpdf2 installation failed (optional)
) else (
    echo SUCCESS: fpdf2 installed
)

echo.
echo Installing free system info library (optional)...
python -m pip install psutil>=5.8.0
if errorlevel 1 (
    echo WARNING: psutil installation failed (optional)
) else (
    echo SUCCESS: psutil installed
)

echo.
echo ================================================
echo Installation completed!
echo Total cost: $0 (completely free)
echo ================================================

echo.
echo Next steps:
echo 1. Test functionality: python tmp_rovodev_free_libraries_compliance.py
echo 2. Run simple installer: python tmp_rovodev_simple_installer.py
echo 3. Check the implementation guide

echo.
echo Press any key to test the installation...
pause >nul

echo.
echo Testing Python imports...
python -c "import sys; print('Python version:', sys.version_info[:3])"
python -c "import cryptography; print('cryptography: OK')" 2>nul || echo "cryptography: MISSING"
python -c "import requests; print('requests: OK')" 2>nul || echo "requests: MISSING"
python -c "import sqlite3; print('sqlite3: OK (built-in)')" 2>nul || echo "sqlite3: MISSING"
python -c "import hashlib; print('hashlib: OK (built-in)')" 2>nul || echo "hashlib: MISSING"

echo.
echo Installation verification completed!
pause