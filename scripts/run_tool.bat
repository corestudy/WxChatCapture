@echo off
chcp 65001 >nul
echo 🚀 智能滚动截图工具启动脚本
echo.

echo 📍 当前目录: %CD%
echo.

echo 🔍 检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo.

echo 📦 检查主程序文件...
if exist "src\main.py" (
    echo ✅ src\main.py 存在
) else (
    echo ❌ src\main.py 不存在
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)
echo.

echo 🚀 启动智能滚动截图工具...
echo.
python src\main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序运行出错，可能的原因：
    echo 1. 缺少依赖包，请运行: pip install -r requirements.txt
    echo 2. Python版本不兼容，需要Python 3.7+
    echo 3. 系统权限问题
    echo.
    pause
)