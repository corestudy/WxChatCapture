#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能滚动截图工具 v3.0 - 主程序

专为微信聊天记录取证和长页面截图而设计的智能截图工具。
提供智能滚动、自动检测、区域选择等高级功能。

作者: 智能截图工具开发团队
版本: 3.0.6
许可: MIT 许可证
"""

# 标准库导入
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

# 第三方库导入
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import numpy as np
from PIL import Image, ImageChops, ImageTk
import cv2

# 项目内模块导入
from advanced_screenshot_manager import AdvancedScreenshotManager
from optimized_recording_manager import AdaptiveRecordingManager
from wechat_detector import WeChatDetector


# 项目配置
__version__ = "3.0.7"
__author__ = "智能截图工具开发团队"

# ===================== 滚动控制模块v2.7 =====================
class ScrollController:
    def __init__(self):
        self.last_scroll_time = 0
        self.stop_flag = threading.Event()
        self.scroll_count = 0

    def reset(self):
        """重置滚动控制器状态"""
        self.scroll_count = 0

    def dynamic_scroll(self, direction, mode, region, app_instance):
        """
        智能滚动控制：v3.0 - Page模式下前3次点击，后续仅滚动
        """
        try:
            x, y, w, h = region
            center_x = x + w // 2
            click_y = y + 5  # 点击区域顶部以避免误触
            
            if w <= 0 or h <= 0:
                app_instance.status_var.set("❌ 滚动区域无效")
                return False

            # Page模式下前3次点击，后续仅滚动
            if mode == "page":
                if self.scroll_count < 3:
                    try:
                        pyautogui.moveTo(center_x, click_y, duration=0.05)
                        pyautogui.click()
                        time.sleep(0.1)
                    except Exception as e:
                        app_instance.status_var.set(f"❌ 窗口激活失败: {str(e)[:30]}")
                        return False
                
                key = "pagedown" if direction == "down" else "pageup"
                pyautogui.press(key)
                self.scroll_count += 1

            # 鼠标模式总是点击和滚动
            elif mode == "mouse":
                try:
                    pyautogui.moveTo(center_x, click_y, duration=0.05)
                    pyautogui.click()
                    time.sleep(0.1)
                except Exception as e:
                    app_instance.status_var.set(f"❌ 窗口激活失败: {str(e)[:30]}")
                    return False
                
                scroll_step = max(3, min(10, h // 100))
                scroll_value = -scroll_step if direction == "down" else scroll_step
                pyautogui.scroll(scroll_value)

            time.sleep(0.4)
            self.last_scroll_time = time.time()
            return True

        except pyautogui.FailSafeException:
            app_instance.status_var.set("🛑 检测到鼠标移至屏幕角落，操作已停止")
            return False
        except Exception as e:
            app_instance.status_var.set(f"❌ 滚动错误: {str(e)[:50]}")
            return False

# ===================== 主应用类v3.0 (集成高级管理器) =====================

class ScrollScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能滚动截图工具 v3.0.8")
        self.root.geometry("1020x810")
        self.root.configure(bg="#f8fafc")
        self.root.resizable(True, True)
        self.root.minsize(960, 700)
        
        # 状态变量
        self.is_capturing = False
        self.is_recording = False
        self.start_x, self.start_y = 0, 0
        self.end_x, self.end_y = 0, 0
        self.region_x, self.region_y = 0, 0
        self.region_width, self.region_height = 0, 0
        self.capture_start_time = 0
        self.capture_count = 0
        
        # 核心组件
        self.scroll_controller = ScrollController()
        self.screenshot_manager = AdvancedScreenshotManager()
        self.recording_manager = AdaptiveRecordingManager()
        
        # UI和样式
        self.setup_styles()
        self.create_scrollable_frame()
        
        # 绑定清理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """关闭窗口时的清理操作"""
        print("正在关闭应用程序...")
        self.screenshot_manager.cleanup()
        self.recording_manager.cleanup()
        self.root.destroy()

    @property
    def region(self):
        return (self.region_x, self.region_y, self.region_width, self.region_height)

    def select_region(self):
        return self.start_region_selection()

    def setup_styles(self):
        self.colors = {
            'primary': '#3b82f6', 'secondary': '#64748b', 'success': '#10b981',
            'warning': '#f59e0b', 'error': '#ef4444', 'bg_light': '#f8fafc',
            'bg_white': '#ffffff', 'text_dark': '#1e293b', 'text_light': '#64748b',
            'border': '#e2e8f0'
        }
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Card.TFrame', background=self.colors['bg_white'], borderwidth=2, relief='solid')
        style.map('Card.TFrame', bordercolor=[('!focus', self.colors['border'])])
        style.configure('Title.TLabel', background=self.colors['bg_white'], foreground=self.colors['text_dark'], font=('Segoe UI', 13, 'bold'))
        style.configure('Subtitle.TLabel', background=self.colors['bg_white'], foreground=self.colors['text_light'], font=('Segoe UI', 9))
        style.configure('Status.TLabel', background=self.colors['bg_white'], foreground=self.colors['text_dark'], font=('Segoe UI', 10))

    def create_scrollable_frame(self):
        main_container = tk.Frame(self.root, bg="#f8fafc")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        canvas = tk.Canvas(main_container, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f8fafc")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.create_modern_ui()

    def create_modern_ui(self):
        title_frame = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        title_frame.pack(fill="x", pady=(0, 20))
        tk.Label(title_frame, text="🚀 智能滚动截图工具", bg="#f8fafc", fg="#1e293b", font=("Segoe UI", 16, "bold")).pack()
        tk.Label(title_frame, text="滚动截图 · 区域录屏 · 证据链记录", bg="#f8fafc", fg="#64748b", font=("Segoe UI", 10)).pack()
        content_frame = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        content_frame.pack(fill='both', expand=True)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        left_column = tk.Frame(content_frame, bg="#f8fafc")
        right_column = tk.Frame(content_frame, bg="#f8fafc")
        left_column.grid(row=0, column=0, sticky='news', padx=(0, 5))
        right_column.grid(row=0, column=1, sticky='news', padx=(5, 0))
        self.create_region_card(left_column)
        self.create_scroll_card(left_column)
        self.create_action_card(left_column)
        self.create_recording_card(right_column)
        self.create_status_card(right_column)
        self.create_save_card(right_column)

    def _create_card(self, parent, icon, text, subtitle, icon_color):
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=20)
        title_frame = tk.Frame(content_frame, bg='#ffffff')
        title_frame.pack(fill='x', anchor='w')
        tk.Label(title_frame, text=icon, bg='#ffffff', fg=icon_color, font=('Segoe UI Emoji', 14, 'bold')).pack(side='left')
        ttk.Label(title_frame, text=text, style='Title.TLabel').pack(side='left', padx=(5,0))
        ttk.Label(content_frame, text=subtitle, style='Subtitle.TLabel').pack(anchor="w", pady=(0, 10))
        return content_frame

    def create_region_card(self, parent):
        content_frame = self._create_card(parent, "📐", "区域选择", "点击“选择区域” → 拖拽框选目标区域", self.colors['primary'])
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x")
        self.select_button = tk.Button(button_frame, text="🎯 选择区域", command=self.start_region_selection, bg=self.colors['primary'], fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8)
        self.select_button.pack(side="left")
        self.detect_button = tk.Button(button_frame, text="🤖 自动检测微信", command=self.auto_detect_wechat_region, bg=self.colors['secondary'], fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8)
        self.detect_button.pack(side="left", padx=(10, 0))
        self.region_info = tk.Label(button_frame, text="未选择区域", bg="#ffffff", fg=self.colors['text_light'], font=("Segoe UI", 9))
        self.region_info.pack(side="left", padx=(15, 0))

    def create_scroll_card(self, parent):
        content_frame = self._create_card(parent, "🖱️", "滚动控制", "模式：鼠标滚轮 / Page 键 · 方向：向下 / 向上", self.colors['warning'])
        mode_frame = tk.Frame(content_frame, bg="#ffffff")
        mode_frame.pack(fill="x", pady=(0, 5))
        tk.Label(mode_frame, text="模式:", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.scroll_mode = tk.StringVar(value="page")    
        tk.Radiobutton(mode_frame, text="Page键", variable=self.scroll_mode, value="page", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        tk.Radiobutton(mode_frame, text="鼠标滚轮", variable=self.scroll_mode, value="mouse", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        direction_frame = tk.Frame(content_frame, bg="#ffffff")
        direction_frame.pack(fill="x", pady=(0, 5))
        tk.Label(direction_frame, text="方向:", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.scroll_direction = tk.StringVar(value="down")
        tk.Radiobutton(direction_frame, text="向下", variable=self.scroll_direction, value="down", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        tk.Radiobutton(direction_frame, text="向上", variable=self.scroll_direction, value="up", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        interval_frame = tk.Frame(content_frame, bg="#ffffff")
        interval_frame.pack(fill="x")
        tk.Label(interval_frame, text="间隔(秒):", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.interval_var = tk.StringVar(value="3")
        tk.Spinbox(interval_frame, from_=0.5, to=10.0, increment=0.5, width=8, textvariable=self.interval_var, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))

    def create_recording_card(self, parent):
        content_frame = self._create_card(parent, "🎥", "屏幕录制", "FPS：10-30 · 区域：选定/全屏", self.colors['error'])
        params_frame = tk.Frame(content_frame, bg="#ffffff")
        params_frame.pack(fill="x", pady=(0, 10))
        tk.Label(params_frame, text="帧率(FPS):", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.fps_var = tk.StringVar(value="30")
        tk.Spinbox(params_frame, from_=5, to=30, increment=5, width=8, textvariable=self.fps_var, font=("Segoe UI", 9)).pack(side="left", padx=(10, 20))
        self.record_region_var = tk.StringVar(value="selected")
        tk.Radiobutton(params_frame, text="选定区域", variable=self.record_region_var, value="selected", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
        tk.Radiobutton(params_frame, text="全屏", variable=self.record_region_var, value="fullscreen", bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left")
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x")
        self.start_record_button = tk.Button(button_frame, text="🔴 开始录制", command=self.start_recording, bg=self.colors['success'], fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8)
        self.start_record_button.pack(side="left", padx=(0, 10))
        self.stop_record_button = tk.Button(button_frame, text="⏹️ 停止录制", command=self.stop_recording, bg=self.colors['error'], fg="white", disabledforeground="#FFFFFF",  font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8, state="disabled")
        self.stop_record_button.pack(side="left")

    def create_status_card(self, parent):
        content_frame = self._create_card(parent, "📊", "状态信息", "显示当前操作状态和结果", self.colors['warning'])
        status_frame = tk.Frame(content_frame, bg="#ffffff")
        status_frame.pack(fill='x', anchor='w')
        self.status_icon = tk.Label(status_frame, text="🔴", font=('Segoe UI Emoji', 12), bg='#ffffff', fg=self.colors['error'])
        self.status_icon.pack(side="left")
        self.status_var = tk.StringVar(value="请先选择截图区域")
        ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel').pack(side="left", padx=(5, 0))
        record_status_frame = tk.Frame(content_frame, bg="#ffffff")
        record_status_frame.pack(fill='x', anchor='w', pady=(5,0))
        self.record_status_icon = tk.Label(record_status_frame, text="⚪", font=('Segoe UI Emoji', 12), bg='#ffffff', fg=self.colors['secondary'])
        self.record_status_icon.pack(side="left")
        self.record_status_var = tk.StringVar(value="未开始录制")
        ttk.Label(record_status_frame, textvariable=self.record_status_var, style='Status.TLabel').pack(side="left", padx=(5, 0))

    def create_action_card(self, parent):
        content_frame = self._create_card(parent, "🎮", "操作控制", "开始或停止截图/滚动", self.colors['success'])
        options_frame = tk.Frame(content_frame, bg="#ffffff")
        options_frame.pack(fill="x", pady=(0,10))
        self.auto_detect = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="智能检测重复内容自动停止", variable=self.auto_detect, bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(anchor="w")
        self.scroll_only = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="纯滚动模式(不截图)", variable=self.scroll_only, bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(anchor="w")
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x", pady=(10,0))
        self.start_button = tk.Button(button_frame, text="🚀 开始截图", command=self.start_capture, bg=self.colors['success'], fg="white", font=("Segoe UI", 12, "bold"), relief="flat", padx=30, pady=12)
        self.start_button.pack(side="left", padx=(0, 10))
        self.stop_button = tk.Button(button_frame, text="⏹️ 停止", command=self.stop_capture, bg=self.colors['error'], fg="white", disabledforeground="#fca5a5", font=("Segoe UI", 12, "bold"), relief="flat", padx=30, pady=12, state="disabled")
        self.stop_button.pack(side="left")

    def create_save_card(self, parent):
        content_frame = self._create_card(parent, "💾", "保存位置", "选择截图和录屏的保存目录", self.colors['primary'])
        path_frame = tk.Frame(content_frame, bg="#ffffff")
        path_frame.pack(fill="x")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_save_path = os.path.join(os.path.dirname(current_dir), "微信聊天记录")
        self.save_path = tk.StringVar(value=default_save_path)
        tk.Entry(path_frame, textvariable=self.save_path, font=("Segoe UI", 9), width=40).pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="📁 更改路径", command=self.browse_save_path, bg=self.colors['secondary'], fg="white", font=("Segoe UI", 9), relief="flat", padx=15, pady=5).pack(side="right", padx=(10, 0))
        tk.Button(path_frame, text="📂 打开文件夹", command=self.open_save_folder, bg=self.colors['secondary'], fg="white", font=("Segoe UI", 9), relief="flat", padx=15, pady=5).pack(side="right", padx=(5, 0))



    def start_region_selection(self):
        """开始区域选择"""
        self.root.withdraw()  # 隐藏主窗口
        self.status_var.set("🎯 请拖拽选择截图区域...")
        
        # 创建全屏透明窗口
        self.selection_window = tk.Toplevel()
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.configure(bg='black')
        self.selection_window.attributes('-topmost', True)
        
        # 绑定鼠标事件
        self.selection_window.bind('<Button-1>', self.on_click)
        self.selection_window.bind('<B1-Motion>', self.on_drag)
        self.selection_window.bind('<ButtonRelease-1>', self.on_release)
        
        # 创建选择矩形
        self.selection_canvas = tk.Canvas(self.selection_window, highlightthickness=0)
        self.selection_canvas.pack(fill='both', expand=True)
        
        self.selection_window.focus_set()

    def on_click(self, event):
        """鼠标点击事件"""
        self.start_x = event.x_root
        self.start_y = event.y_root

    def on_drag(self, event):
        """鼠标拖拽事件"""
        self.end_x = event.x_root
        self.end_y = event.y_root
        
        # 清除之前的矩形
        self.selection_canvas.delete("selection")
        
        # 绘制新矩形
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
        
        self.selection_canvas.create_rectangle(x1, y1, x2, y2, 
                                             outline='red', width=2, tags="selection")

    def on_release(self, event):
        """鼠标释放事件"""
        self.end_x = event.x_root
        self.end_y = event.y_root
        
        # 计算选择区域
        self.region_x = min(self.start_x, self.end_x)
        self.region_y = min(self.start_y, self.end_y)
        self.region_width = abs(self.end_x - self.start_x)
        self.region_height = abs(self.end_y - self.start_y)
        
        # 关闭选择窗口
        self.selection_window.destroy()
        self.root.deiconify()  # 显示主窗口
        
        # 更新界面信息
        if self.region_width > 50 and self.region_height > 50:
            self.region_info.config(text=f"区域: {self.region_width}×{self.region_height}")
            self.status_var.set("✅ 区域选择完成，可以开始截图")
            self.status_icon.config(text="🟢")
            self.start_button.config(state="normal")
            
            # 滚动步长由区域高度自动设置，不再需要手动设置
        else:
            self.status_var.set("❌ 选择区域过小，请重新选择")
            self.status_icon.config(text="🔴")

    def auto_detect_wechat_region(self):
        """自动检测微信窗口和聊天区域"""
        self.status_var.set("🔍 正在检测微信窗口...")
        self.root.update_idletasks() # 更新UI

        try:
            detector = WeChatDetector()
            if not detector.find_wechat_window():
                messagebox.showwarning("检测失败", "未找到正在运行的微信客户端。")
                self.status_var.set("❌ 未找到微信窗口")
                return

            self.status_var.set("✅ 找到微信窗口，正在分析布局...")
            self.root.update_idletasks()

            if not detector.detect_chat_layout():
                messagebox.showwarning("检测失败", "无法智能识别微信的聊天区域布局。")
                self.status_var.set("❌ 无法识别聊天区域")
                return

            region = detector.get_optimal_capture_region()
            if not region:
                messagebox.showerror("检测失败", "成功分析布局，但无法获取最佳截图区域。")
                self.status_var.set("❌ 获取截图区域失败")
                return

            # 更新区域变量
            self.region_x, self.region_y, self.region_width, self.region_height = region
            
            # 更新UI
            self.region_info.config(text=f"区域: {self.region_width}×{self.region_height}")
            self.status_var.set("✅ 成功检测到微信聊天区域！")
            self.status_icon.config(text="🟢")
            self.start_button.config(state="normal")
            messagebox.showinfo("检测成功", f"已自动为您选择微信聊天区域，尺寸为 {self.region_width}×{self.region_height}。")

        except Exception as e:
            messagebox.showerror("严重错误", f"微信检测过程中发生未知错误: {e}")
            self.status_var.set(f"❌ 检测时发生严重错误")

    def browse_save_path(self):
        """浏览保存路径"""
        try:
            initial_dir = self.save_path.get()
            if not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")  # 使用用户主目录作为默认
            path = filedialog.askdirectory(parent=self.root, initialdir=initial_dir, title="选择保存位置")
            if path:
                self.save_path.set(path)
                self.status_var.set(f"✅ 保存位置已更新: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件浏览器: {str(e)}")
            self.status_var.set("❌ 文件浏览器打开失败")

    def start_capture(self):
        """开始截图 (高级版)"""
        if self.region_width <= 0 or self.region_height <= 0:
            messagebox.showerror("错误", "请先选择截图区域")
            return
        
        # 创建保存目录
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.screenshot_manager.set_save_directory(save_dir) # 设置保存目录
        
        self.scroll_controller.reset() # 重置滚动计数器
        self.is_capturing = True
        self.capture_count = 0
        self.capture_start_time = time.time()
        self.screenshot_manager.stats['duplicates_detected'] = 0 # 重置计数

        # 更新界面状态
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("🚀 启动高级截图引擎...")
        self.status_icon.config(text="🟡")
        
        # 启动截图线程
        threading.Thread(target=self.capture_process_advanced, daemon=True).start()

    def capture_process_advanced(self):
        """使用高级管理器进行截图处理 (v3.2 - 重构循环以消除竞争条件)"""
        # 第一次截图总是在滚动之前
        if not self.scroll_only.get():
            self.screenshot_manager.capture_screenshot_async(self.region, self.screenshot_callback)

        while self.is_capturing:
            # 1. 更新UI
            elapsed = time.time() - self.capture_start_time
            self.root.after(0, lambda: self.status_var.set(
                f"📸 已捕获 {self.capture_count} 张 | 重复 {self.screenshot_manager.stats['duplicates_detected']} | {elapsed:.1f}s"))

            # 2. 滚动
            scroll_mode = self.scroll_mode.get()
            scroll_direction = self.scroll_direction.get()
            if not self.scroll_controller.dynamic_scroll(scroll_direction, scroll_mode, self.region, self):
                self.root.after(0, lambda: self.status_var.set("❌ 滚动失败，自动停止"))
                break

            # 3. 等待内容加载
            wait_time = float(self.interval_var.get())
            time.sleep(wait_time)

            # 在等待后检查是否被外部停止
            if not self.is_capturing:
                break

            # 4. 截图
            if not self.scroll_only.get():
                self.screenshot_manager.capture_screenshot_async(self.region, self.screenshot_callback)

        # 循环结束后，安排最终的清理工作
        self.root.after(0, self.stop_capture)

    def screenshot_callback(self, screenshot, task, success, result):
        """处理异步截图结果的回调函数 (v3.2 - 简化)"""
        if not self.is_capturing:
            return

        if success:
            self.capture_count += 1
        elif result == "重复内容":
            if self.auto_detect.get():
                self.root.after(0, lambda: self.status_var.set("🎯 检测到重复内容，自动停止"))
                self.is_capturing = False # 停止循环
        else:
            print(f"截图任务失败: {result}")

    def stop_capture(self):
        """停止截图 (v3.1 - 确保UI总能重置)"""
        if not self.is_capturing:
            # 即使已经停止，也确保UI状态正确
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            return

        self.is_capturing = False
        self.scroll_controller.stop_flag.set()
        
        # 重置界面状态
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # 检查状态变量，避免覆盖“自动停止”的消息
        final_message = self.status_var.get()
        if "自动停止" in final_message:
            pass # 保持现有消息
        elif self.capture_count > 0:
            elapsed = time.time() - self.capture_start_time
            self.status_var.set(f"✅ 完成！共截图 {self.capture_count} 张，用时 {elapsed:.1f}s")
            self.status_icon.config(text="🟢")
        else:
            self.status_var.set("⏹️ 已停止")
            self.status_icon.config(text="🟡")

    def start_recording(self):
        """开始屏幕录制 (高级版)"""
        if self.is_recording:
            messagebox.showwarning("警告", "录制已在进行中")
            return

        # 检查区域选择
        if self.record_region_var.get() == "selected":
            if self.region_width <= 0 or self.region_height <= 0:
                messagebox.showerror("错误", "请先选择录制区域")
                return
            record_region = self.region
        else:
            # 全屏录制
            screen_size = pyautogui.size()
            record_region = (0, 0, screen_size.width, screen_size.height)

        # 创建录制目录
        save_dir = Path(self.save_path.get())
        record_dir = save_dir / "录制视频"
        record_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screen_record_{timestamp}.mp4"
        output_path = str(record_dir / filename)

        # 设置录制参数
        self.recording_manager.fps = int(self.fps_var.get())

        # 开始录制
        if not self.recording_manager.start_recording(record_region, output_path):
            messagebox.showerror("错误", "无法启动录制器，请查看控制台日志。")
            return

        self.is_recording = True
        # 更新UI状态
        self.start_record_button.config(state="disabled")
        self.stop_record_button.config(state="normal")
        self.record_status_var.set("🔴 正在录制...")
        self._update_recording_status()
        messagebox.showinfo("录制开始", f"开始录制到:\n{output_path}")

    def stop_recording(self):
        """停止屏幕录制 (高级版)"""
        if not self.is_recording:
            return

        stats = self.recording_manager.stop_recording()
        self.is_recording = False

        # 更新UI状态
        self.start_record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        
        if stats and stats.get('file_exists'):
            duration = stats.get('total_recording_time', 0)
            size_mb = stats.get('file_size_mb', 0)
            self.record_status_var.set(f"✅ 录制完成 | {duration:.1f}s | {size_mb:.1f}MB")
            
            msg = (
                f"录制已完成!\n"
                f"文件: {stats.get('output_path')}\n"
                f"时长: {duration:.1f}秒\n"
                f"大小: {size_mb:.1f}MB"
            )
            messagebox.showinfo("录制完成", msg)
        else:
            self.record_status_var.set("⏹️ 录制已停止，但未生成文件。")

    def _update_recording_status(self):
        """更新录制状态显示"""
        if self.is_recording:
            stats = self.recording_manager.get_current_stats()
            duration = stats.get('current_recording_time', 0)
            fps = stats.get('current_fps', 0)
            self.record_status_var.set(f"🔴 录制中... | {duration:.1f}s | {fps:.1f} FPS")
            # 每秒更新一次
            self.root.after(1000, self._update_recording_status)

    def open_save_folder(self):
        """打开保存文件夹，如果不存在则创建"""
        save_dir = Path(self.save_path.get())
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            if os.name == 'nt':  # Windows
                os.startfile(str(save_dir))
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{save_dir}"' if sys.platform == 'darwin' else f'xdg-open "{save_dir}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")

def main():
    root = tk.Tk()
    app = ScrollScreenshotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()