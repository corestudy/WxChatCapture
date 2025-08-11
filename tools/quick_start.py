#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动工具 - 简化的启动和诊断脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def quick_check():
    """快速检查"""
    print("🔍 快速检查...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print(f"❌ Python版本过低: {sys.version_info.major}.{sys.version_info.minor}")
        print("需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 检查主程序文件
    main_file = os.path.join(project_root, 'src', 'main.py')
    if not os.path.exists(main_file):
        print("❌ 找不到主程序文件: src/main.py")
        print("请确保在项目根目录运行此脚本")
        return False
    
    print("✅ 找到主程序文件")
    
    # 快速检查关键依赖
    critical_deps = ['tkinter', 'PIL', 'pyautogui']
    for dep in critical_deps:
        try:
            if dep == 'PIL':
                from PIL import Image
            else:
                __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} 未安装")
            return False
    
    return True

def quick_start():
    """快速启动"""
    print("\n🚀 启动程序...")
    
    try:
        from src.main import ScrollScreenshotApp
        import tkinter as tk
        
        # 创建并运行应用
        root = tk.Tk()
        app = ScrollScreenshotApp(root)
        
        print("✅ 程序启动成功!")
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n💡 解决方案:")
        print("1. 安装依赖包: pip install pillow pyautogui numpy pywinauto keyboard opencv-python")
        print("2. 或运行: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("\n💡 可能的原因:")
        print("1. 缺少必要的系统权限")
        print("2. 显示器配置问题")
        print("3. 依赖包版本不兼容")

def main():
    """主函数"""
    print("🚀 智能滚动截图工具 v3.0.6 - 快速启动")
    print("=" * 50)
    
    # 快速检查
    if not quick_check():
        print("\n❌ 检查失败，无法启动程序")
        print("请运行 tools/debug_run.py 获取详细信息")
        input("按回车键退出...")
        return
    
    print("\n✅ 检查通过!")
    
    # 快速启动
    quick_start()

if __name__ == "__main__":
    main()