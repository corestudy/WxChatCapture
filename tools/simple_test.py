#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试工具 - 提供可视化的测试界面
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class SimpleTestGUI:
    """简单测试GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("智能滚动截图工具 - 简单测试")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 标题
        title_label = tk.Label(
            self.root, 
            text="智能滚动截图工具测试", 
            font=("Arial", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # 状态显示
        self.status_text = tk.Text(
            self.root, 
            height=8, 
            width=45,
            font=("Consolas", 9),
            bg="#f0f0f0"
        )
        self.status_text.pack(pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 测试按钮
        test_btn = tk.Button(
            button_frame,
            text="🔍 运行测试",
            command=self.run_tests,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        )
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # 启动主程序按钮
        start_btn = tk.Button(
            button_frame,
            text="🚀 启动主程序",
            command=self.start_main_program,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        quit_btn = tk.Button(
            button_frame,
            text="❌ 退出",
            command=self.root.quit,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=5
        )
        quit_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始信息
        self.log("🎉 测试界面已就绪")
        self.log("点击 '运行测试' 开始检查系统")
    
    def log(self, message):
        """记录日志"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def run_tests(self):
        """运行测试"""
        self.status_text.delete(1.0, tk.END)
        self.log("🔍 开始运行测试...")
        
        # 测试1: Python版本
        self.log(f"Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        # 测试2: 基础依赖
        self.log("检查基础依赖...")
        deps = [
            ("tkinter", "import tkinter"),
            ("PIL", "from PIL import Image"),
            ("pyautogui", "import pyautogui"),
            ("numpy", "import numpy"),
        ]
        
        failed_deps = []
        for name, import_cmd in deps:
            try:
                exec(import_cmd)
                self.log(f"  ✅ {name}")
            except ImportError:
                self.log(f"  ❌ {name}")
                failed_deps.append(name)
        
        # 测试3: 主程序
        self.log("检查主程序...")
        try:
            from src.main import ScrollScreenshotApp
            self.log("  ✅ 主程序导入成功")
            main_ok = True
        except Exception as e:
            self.log(f"  ❌ 主程序导入失败: {e}")
            main_ok = False
        
        # 测试结果
        self.log("\n" + "="*40)
        if failed_deps:
            self.log(f"❌ 测试失败! 缺少依赖: {', '.join(failed_deps)}")
            self.log("请运行: pip install pillow pyautogui numpy")
        elif not main_ok:
            self.log("❌ 主程序有问题!")
        else:
            self.log("✅ 所有测试通过!")
            self.log("可以启动主程序了!")
    
    def start_main_program(self):
        """启动主程序"""
        try:
            self.log("🚀 正在启动主程序...")
            self.root.withdraw()  # 隐藏测试窗口
            
            from src.main import ScrollScreenshotApp
            
            main_root = tk.Tk()
            app = ScrollScreenshotApp(main_root)
            
            self.log("✅ 主程序启动成功!")
            
            # 当主程序关闭时，显示测试窗口
            def on_main_close():
                self.root.deiconify()
                self.log("主程序已关闭")
            
            main_root.protocol("WM_DELETE_WINDOW", lambda: [main_root.destroy(), on_main_close()])
            main_root.mainloop()
            
        except Exception as e:
            self.root.deiconify()  # 显示测试窗口
            self.log(f"❌ 启动失败: {e}")
            messagebox.showerror("启动失败", f"无法启动主程序:\n{e}")
    
    def run(self):
        """运行测试GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🧪 启动简单测试界面...")
    
    try:
        test_gui = SimpleTestGUI()
        test_gui.run()
    except Exception as e:
        print(f"❌ 测试界面启动失败: {e}")
        print("可能的原因:")
        print("1. tkinter未正确安装")
        print("2. 显示器配置问题")
        print("3. Python环境问题")
        input("按回车键退出...")

if __name__ == "__main__":
    main()