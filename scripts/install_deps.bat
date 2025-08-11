@echo off
chcp 65001 >nul
echo 📦 安装智能滚动截图工具依赖包
echo.

echo 🔍 检查pip...
pip --version
if %errorlevel% neq 0 (
    echo ❌ pip未安装或未添加到PATH
    pause
    exit /b 1
)
echo.

echo 📋 安装依赖包...
echo.

echo 安装核心依赖...
pip install pillow>=9.0.0
pip install pyautogui>=0.9.54
pip install numpy>=1.21.0
pip install pywinauto>=0.6.8
pip install keyboard>=0.13.5

echo.
echo 安装扩展功能依赖...
pip install opencv-python>=4.5.0
pip install psutil>=5.8.0

echo.
echo ✅ 依赖包安装完成！
echo.
echo 🚀 现在可以运行程序了:
echo python src\main.py
echo.
pause