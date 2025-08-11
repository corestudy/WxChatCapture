#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的主程序
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """测试所有导入"""
    try:
        print("🔍 测试导入...")
        
        # 测试OpenCV
        import cv2
        print(f"✅ OpenCV 导入成功 - 版本: {cv2.__version__}")
        
        # 测试其他依赖
        import tkinter as tk
        import numpy as np
        from PIL import Image
        import pyautogui
        from datetime import datetime
        from pathlib import Path
        
        print("✅ 所有基础依赖导入成功")
        
        # 测试主程序导入
        from src.main import ScrollScreenshotApp
        print("✅ 主程序类导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_app_creation():
    """测试应用创建"""
    try:
        print("\n🚀 测试应用创建...")
        
        import tkinter as tk
        from src.main import ScrollScreenshotApp
        
        # 创建根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建应用
        app = ScrollScreenshotApp(root)
        print("✅ 应用创建成功")
        
        # 检查录屏相关属性
        if hasattr(app, 'is_recording'):
            print("✅ 录屏属性存在")
        else:
            print("❌ 录屏属性缺失")
            
        # 检查录屏方法
        if hasattr(app, 'start_recording'):
            print("✅ 录屏方法存在")
        else:
            print("❌ 录屏方法缺失")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 录屏功能修复测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖安装")
        return False
    
    # 测试应用创建
    if not test_app_creation():
        print("\n❌ 应用创建测试失败")
        return False
    
    print("\n✅ 所有测试通过！")
    print("现在可以运行主程序:")
    print("python src/main.py")
    
    return True

if __name__ == "__main__":
    main()