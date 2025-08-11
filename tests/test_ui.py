# UI测试文件 - 测试智能滚动截图工具的用户界面
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的UI界面
"""

import tkinter as tk
from src.main import ScrollScreenshotApp

def test_ui():
    """测试UI界面"""
    try:
        root = tk.Tk()
        app = ScrollScreenshotApp(root)
        
        print("✅ UI界面加载成功！")
        print("🎨 现代化界面特性：")
        print("  • 响应式布局设计")
        print("  • 现代化配色方案")
        print("  • 丰富的图标系统")
        print("  • 智能状态指示")
        print("  • 增强的错误处理")
        
        # 启动界面
        root.mainloop()
        
    except Exception as e:
        print(f"❌ UI测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_ui()