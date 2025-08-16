#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查工具 - 检查所有必需的依赖包
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_dependencies():
    """检查所有依赖包"""
    print("🔍 检查依赖包...")
    print("=" * 50)
    
    # 基础依赖列表
    dependencies = [
        ("tkinter", "GUI框架"),
        ("PIL", "图像处理 (Pillow)"),
        ("pyautogui", "屏幕控制"),
        ("numpy", "数值计算"),
        ("pywinauto", "Windows自动化"),
        ("keyboard", "键盘控制"),
        ("cv2", "视频处理 (OpenCV)")
    ]
    
    failed_deps = []
    
    for dep_name, description in dependencies:
        try:
            if dep_name == "PIL":
                from PIL import Image, ImageTk
            elif dep_name == "cv2":
                import cv2
            else:
                __import__(dep_name)
            print(f"✅ {dep_name:12} - {description}")
        except ImportError as e:
            print(f"❌ {dep_name:12} - {description} (导入失败: {e})")
            failed_deps.append(dep_name)
        except Exception as e:
            print(f"⚠️  {dep_name:12} - {description} (其他错误: {e})")
            failed_deps.append(dep_name)
    
    print("=" * 50)
    
    if failed_deps:
        print(f"❌ 发现 {len(failed_deps)} 个依赖问题:")
        for dep in failed_deps:
            print(f"   - {dep}")
        print("\n💡 解决方案:")
        print("pip install pillow pyautogui numpy opencv-python")
        return False
    else:
        print("✅ 所有依赖检查通过!")
        return True

def check_main_program():
    """检查主程序"""
    print("\n🚀 检查主程序...")
    try:
        from src.main import ScrollScreenshotApp
        print("✅ 主程序导入成功")
        return True
    except ImportError as e:
        print(f"❌ 主程序导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 主程序检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 智能滚动截图工具 - 依赖检查")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 检查主程序
    main_ok = check_main_program()
    
    print("\n" + "=" * 50)
    if deps_ok and main_ok:
        print("🎉 所有检查通过! 可以正常运行程序")
        print("运行命令: python src/main.py  | 文档: docs_unified/README.md")
    else:
        print("❌ 检查未通过，请解决上述问题后重试")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()