#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试运行工具 - 提供详细的错误信息和调试功能
"""

import sys
import traceback
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def print_system_info():
    """打印系统信息"""
    print("🖥️ 系统信息:")
    print(f"   Python版本: {sys.version}")
    print(f"   Python路径: {sys.executable}")
    print(f"   当前目录: {os.getcwd()}")
    print(f"   项目根目录: {project_root}")
    print()

def check_dependencies_detailed():
    """详细检查依赖"""
    print("📦 详细依赖检查:")
    
    dependencies = [
        ("tkinter", "import tkinter as tk"),
        ("PIL", "from PIL import Image, ImageTk"),
        ("pyautogui", "import pyautogui"),
        ("numpy", "import numpy as np"),
        ("pywinauto", "from pywinauto import Desktop"),
        ("keyboard", "import keyboard"),
        ("cv2", "import cv2"),
        ("threading", "import threading"),
        ("datetime", "from datetime import datetime"),
        ("pathlib", "from pathlib import Path")
    ]
    
    failed_count = 0
    
    for name, import_cmd in dependencies:
        try:
            exec(import_cmd)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name}: {e}")
            failed_count += 1
        except Exception as e:
            print(f"   ⚠️  {name}: {e}")
            failed_count += 1
    
    print(f"\n   总计: {len(dependencies) - failed_count}/{len(dependencies)} 通过")
    return failed_count == 0

def test_main_program():
    """测试主程序"""
    print("\n🚀 测试主程序:")
    
    try:
        print("   导入主程序模块...")
        from src.main import ScrollScreenshotApp
        print("   ✅ 主程序模块导入成功")
        
        print("   创建Tkinter窗口...")
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        print("   ✅ Tkinter窗口创建成功")
        
        print("   创建应用实例...")
        app = ScrollScreenshotApp(root)
        print("   ✅ 应用实例创建成功")
        
        print("   检查核心功能...")
        # 检查关键属性和方法
        # 兼容老/新接口命名
        required_attrs = ['is_capturing', 'save_path']
        alt_region = ['region']  # @property 存在于实例上
        required_methods = ['start_capture', 'stop_capture']
        alt_select = ['select_region', 'start_region_selection']
        
        for attr in required_attrs:
            if hasattr(app, attr):
                print(f"   ✅ 属性 {attr} 存在")
            else:
                print(f"   ❌ 属性 {attr} 缺失")

        # 兼容 region 属性（可能为 @property）
        if any(hasattr(app, a) for a in alt_region):
            print("   ✅ 属性 region 存在")
        else:
            print("   ❌ 属性 region 缺失")
        
        for method in required_methods:
            if hasattr(app, method):
                print(f"   ✅ 方法 {method} 存在")
            else:
                print(f"   ❌ 方法 {method} 缺失")

        # 兼容选择区域的两种方法名
        if any(hasattr(app, m) for m in alt_select):
            print("   ✅ 方法 select_region/start_region_selection 存在")
        else:
            print("   ❌ 方法 select_region/start_region_selection 缺失")
        
        root.destroy()
        print("   ✅ 主程序测试完成")
        return True
        
    except Exception as e:
        print(f"   ❌ 主程序测试失败: {e}")
        print("\n📋 详细错误信息:")
        traceback.print_exc()
        return False

def run_main_program():
    """运行主程序"""
    print("\n🎉 启动主程序...")
    
    try:
        from src.main import ScrollScreenshotApp
        import tkinter as tk
        
        root = tk.Tk()
        app = ScrollScreenshotApp(root)
        
        print("✅ 程序启动成功! 正在显示界面...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ 程序运行失败: {e}")
        print("\n📋 详细错误信息:")
        traceback.print_exc()
        
        print("\n💡 可能的解决方案:")
        if "ModuleNotFoundError" in str(type(e)):
            print("1. 安装缺失的模块: pip install pillow pyautogui numpy opencv-python")
        elif "tkinter" in str(e).lower():
            print("1. Tkinter问题，可能需要重新安装Python")
        else:
            print("1. 检查Python版本是否为3.7+")
            print("2. 确保所有依赖包已正确安装")
            print("3. 检查系统权限设置")

def main():
    """主函数"""
    print("🔧 智能滚动截图工具 - 调试运行")
    print("=" * 60)
    
    # 打印系统信息
    print_system_info()
    
    # 检查依赖
    deps_ok = check_dependencies_detailed()
    
    if not deps_ok:
        print("\n❌ 依赖检查失败，请先解决依赖问题")
        input("按回车键退出...")
        return
    
    # 测试主程序
    main_ok = test_main_program()
    
    if not main_ok:
        print("\n❌ 主程序测试失败")
        input("按回车键退出...")
        return
    
    # 询问是否运行主程序
    print("\n" + "=" * 60)
    choice = input("所有测试通过! 是否启动主程序? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是', '']:
        run_main_program()
    else:
        print("调试完成，可以手动运行: python src/main.py")

if __name__ == "__main__":
    main()