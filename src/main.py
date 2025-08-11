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
from pywinauto import Desktop
import cv2
import keyboard

# 项目配置
__version__ = "3.0.6"
__author__ = "智能截图工具开发团队"

# ===================== 滚动控制模块v2.6 =====================
# 激活指定坐标点所在的窗口，确保后续滚动操作生效
def activate_window_by_point(x, y):
    try:
        windows = Desktop(backend='uia').windows()
        for w in windows:
            rect = w.rectangle()
            if rect.left <= x <= rect.right and rect.top <= y <= rect.bottom:
                w.set_focus()
                w.set_focus()  # 多调用一次以确保
                return True
    except Exception as e:
        print(f'窗口激活失败: {e}')
    return False

class ScrollController:
    def __init__(self):
        self.last_scroll_time = 0
        self.stop_flag = threading.Event()
        self.page_mode_activated = False  # Page键模式下是否已激活窗口
    
    def dynamic_scroll(self, direction, mode, region, app_instance):
        """
        智能滚动控制：支持Page键和鼠标滚轮两种模式
        增加错误处理和重试机制
        """
        try:
            x, y, w, h = region
            # 根据区域高度自动计算滚动步长
            scroll_step = max(3, min(10, h // 100))
            center_x = x + w // 2
            
            # 检查区域有效性
            if w <= 0 or h <= 0:
                app_instance.status_var.set("❌ 滚动区域无效")
                return False
            
            if mode == "page":
                center_y = y + h // 2
                if not self.page_mode_activated:
                    # 智能窗口激活 - 增加重试机制
                    for attempt in range(3):
                        try:
                            pyautogui.moveTo(center_x, center_y, duration=0.1)
                            pyautogui.click()
                            if activate_window_by_point(center_x, center_y):
                                break
                            time.sleep(0.5)  # 等待窗口激活
                        except Exception as e:
                            if attempt == 2:  # 最后一次尝试失败
                                app_instance.status_var.set(f"❌ 窗口激活失败: {str(e)[:30]}")
                                return False
                    
                    # 确保焦点在正确位置
                    pyautogui.moveTo(center_x, y + 10, duration=0.1)
                    pyautogui.click()
                    self.page_mode_activated = True
                    app_instance.status_var.set("✅ 窗口已激活，开始Page键滚动")
                
                # 发送Page键
                key = "pagedown" if direction == "down" else "pageup"
                keyboard.send(key)
                
            elif mode == "mouse":
                center_y = y + h // 2
                # 移动到滚动区域中心
                pyautogui.moveTo(center_x, center_y, duration=0.1)
                
                # 激活窗口
                for attempt in range(2):
                    try:
                        pyautogui.click()
                        if activate_window_by_point(center_x, center_y):
                            break
                    except Exception as e:
                        if attempt == 1:
                            app_instance.status_var.set(f"❌ 鼠标滚动激活失败: {str(e)[:30]}")
                            return False
                
                # 执行滚动
                scroll_value = -scroll_step if direction == "down" else scroll_step
                pyautogui.scroll(scroll_value)
                
            # 智能等待页面响应 - 根据模式优化
            if mode == "page":
                time.sleep(0.5)  # Page键响应快
            else:
                time.sleep(0.3)  # 鼠标滚轮响应更快
            
            self.last_scroll_time = time.time()
            return True
            
        except pyautogui.FailSafeException:
            app_instance.status_var.set("🛑 检测到鼠标移至屏幕角落，操作已停止")
            return False
        except Exception as e:
            app_instance.status_var.set(f"❌ 滚动错误: {str(e)[:50]}")
            return False

# ===================== 主应用类v2.7 (UI优化) =====================
class ScrollScreenshotApp:
    def __init__(self, root):
        """
        初始化主界面和状态变量，创建UI。
        """
        self.root = root
        self.root.title("🚀 智能滚动截图工具 v3.0")
        self.root.geometry("520x850")  # 稍微增大窗口
        self.root.configure(bg="#f8fafc") # 更清爽的背景色
        self.root.resizable(True, True) # 允许调整窗口大小
        self.root.minsize(480, 700)  # 设置最小尺寸
        self.is_capturing = False
        self.start_x, self.start_y = 0, 0
        self.end_x, self.end_y = 0, 0
        self.region_x, self.region_y = 0, 0  # 选区左上角
        self.region_width, self.region_height = 0, 0  # 选区宽高
        self.capture_start_time = 0
        self.capture_count = 0
        self.last_screenshot = None
        self.scroll_controller = ScrollController()
        # 滚动步长由区域高度自动计算，不再需要手动设置
        self.page_mode_activated = False  # Page键模式下窗口激活标志
        
        # 录屏功能相关
        self.is_recording = False
        self.video_writer = None
        self.record_thread = None
        self.recording_start_time = None
        self.recording_fps = 10
        self.recording_codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.setup_styles()
        self.create_scrollable_frame()

    def setup_styles(self):
        """设置现代化UI样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 定义颜色方案
        colors = {
            'primary': '#3b82f6',
            'secondary': '#64748b', 
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'bg_light': '#f8fafc',
            'bg_white': '#ffffff',
            'text_dark': '#1e293b',
            'text_light': '#64748b'
        }
        
        # 配置样式
        style.configure('Card.TFrame', background=colors['bg_white'], relief='solid', borderwidth=1)
        style.configure('Title.TLabel', background=colors['bg_white'], foreground=colors['text_dark'], 
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Subtitle.TLabel', background=colors['bg_white'], foreground=colors['text_light'], 
                       font=('Segoe UI', 9))
        style.configure('Status.TLabel', background=colors['bg_light'], foreground=colors['text_dark'], 
                       font=('Segoe UI', 10))
        style.configure('Preview.TLabel', background=colors['bg_white'], foreground=colors['text_light'], 
                       font=('Segoe UI', 9), anchor='center')

    def create_scrollable_frame(self):
        """创建可滚动的主框架"""
        # 创建主容器
        main_container = tk.Frame(self.root, bg="#f8fafc")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(main_container, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f8fafc")
        
        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 创建UI内容
        self.create_modern_ui()

    def create_modern_ui(self):
        """创建现代化UI界面"""
        # 标题区域
        title_frame = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🚀 智能滚动截图工具 v3.0", 
                              bg="#f8fafc", fg="#1e293b", font=("Segoe UI", 16, "bold"))
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="专为微信聊天记录取证和长页面截图而设计", 
                                 bg="#f8fafc", fg="#64748b", font=("Segoe UI", 10))
        subtitle_label.pack()
        
        # 区域选择卡片
        self.create_region_card()
        
        # 滚动控制卡片  
        self.create_scroll_card()
        
        # 截图控制卡片
        self.create_capture_card()
        
        # 录屏控制卡片
        self.create_recording_card()
        
        # 保存位置卡片
        self.create_save_card()
        
        # 状态显示卡片
        self.create_status_card()
        
        # 预览卡片已删除 - 提升性能
        
        # 操作按钮
        self.create_action_buttons()

    def create_region_card(self):
        """创建区域选择卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        # 卡片内容
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 标题
        title_label = ttk.Label(content_frame, text="📐 区域选择", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(content_frame, text="拖拽选择截图区域", style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w", pady=(0, 10))
        
        # 按钮和信息
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x")
        
        self.select_button = tk.Button(button_frame, text="🎯 选择区域", 
                                      command=self.start_region_selection,
                                      bg="#3b82f6", fg="white", font=("Segoe UI", 10, "bold"),
                                      relief="flat", padx=20, pady=8)
        self.select_button.pack(side="left")
        
        self.region_info = tk.Label(button_frame, text="未选择区域", 
                                   bg="#ffffff", fg="#64748b", font=("Segoe UI", 9))
        self.region_info.pack(side="left", padx=(15, 0))

    def create_scroll_card(self):
        """创建滚动控制卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(content_frame, text="🖱️ 滚动控制", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(content_frame, text="选择滚动模式和参数", style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w", pady=(0, 10))
        
        # 滚动模式
        mode_frame = tk.Frame(content_frame, bg="#ffffff")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(mode_frame, text="滚动模式:", bg="#ffffff", fg="#1e293b", 
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.scroll_mode = tk.StringVar(value="mouse")
        tk.Radiobutton(mode_frame, text="🖱️ 鼠标滚轮", variable=self.scroll_mode, value="mouse",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        tk.Radiobutton(mode_frame, text="📄 Page键", variable=self.scroll_mode, value="page",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        
        # 滚动方向
        direction_frame = tk.Frame(content_frame, bg="#ffffff")
        direction_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(direction_frame, text="滚动方向:", bg="#ffffff", fg="#1e293b", 
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.scroll_direction = tk.StringVar(value="down")
        tk.Radiobutton(direction_frame, text="⬇️ 向下", variable=self.scroll_direction, value="down",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
        tk.Radiobutton(direction_frame, text="⬆️ 向上", variable=self.scroll_direction, value="up",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))

    def create_capture_card(self):
        """创建截图控制卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(content_frame, text="📸 截图控制", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(content_frame, text="设置截图参数和模式", style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w", pady=(0, 10))
        
        # 间隔时间
        interval_frame = tk.Frame(content_frame, bg="#ffffff")
        interval_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(interval_frame, text="间隔时间(秒):", bg="#ffffff", fg="#1e293b", 
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.interval_var = tk.StringVar(value="0.3")
        interval_spinbox = tk.Spinbox(interval_frame, from_=0.1, to=5.0, increment=0.1, 
                                     width=8, textvariable=self.interval_var, font=("Segoe UI", 9))
        interval_spinbox.pack(side="left", padx=(10, 0))
        
        # 检测选项
        options_frame = tk.Frame(content_frame, bg="#ffffff")
        options_frame.pack(fill="x")
        
        self.auto_detect = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🔍 智能检测重复内容自动停止", 
                      variable=self.auto_detect, bg="#ffffff", fg="#1e293b", 
                      font=("Segoe UI", 9)).pack(anchor="w")
        
        self.scroll_only = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="📜 纯滚动模式(不截图)", 
                      variable=self.scroll_only, bg="#ffffff", fg="#1e293b", 
                      font=("Segoe UI", 9)).pack(anchor="w")

    def create_recording_card(self):
        """创建录屏控制卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(content_frame, text="🎥 屏幕录制", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(content_frame, text="录制选定区域的屏幕活动", style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w", pady=(0, 10))
        
        # 录制状态显示
        status_frame = tk.Frame(content_frame, bg="#ffffff")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.record_status_var = tk.StringVar(value="⚪ 未开始录制")
        self.record_status_label = tk.Label(status_frame, textvariable=self.record_status_var, 
                                          bg="#ffffff", fg="#1e293b", font=("Segoe UI", 10, "bold"))
        self.record_status_label.pack(side="left")
        
        # 录制参数设置
        params_frame = tk.Frame(content_frame, bg="#ffffff")
        params_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(params_frame, text="帧率(FPS):", bg="#ffffff", fg="#1e293b", 
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.fps_var = tk.StringVar(value="10")
        fps_spinbox = tk.Spinbox(params_frame, from_=5, to=30, increment=5, 
                               width=8, textvariable=self.fps_var, font=("Segoe UI", 9))
        fps_spinbox.pack(side="left", padx=(10, 20))
        
        # 录制区域选项
        self.record_region_var = tk.StringVar(value="selected")
        tk.Radiobutton(params_frame, text="🎯 选定区域", variable=self.record_region_var, value="selected",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))
        tk.Radiobutton(params_frame, text="🖥️ 全屏", variable=self.record_region_var, value="fullscreen",
                      bg="#ffffff", fg="#1e293b", font=("Segoe UI", 9)).pack(side="left")
        
        # 录制控制按钮
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x")
        
        self.start_record_button = tk.Button(button_frame, text="🔴 开始录制", 
                                           command=self.start_recording,
                                           bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"),
                                           relief="flat", padx=20, pady=8)
        self.start_record_button.pack(side="left", padx=(0, 10))
        
        self.stop_record_button = tk.Button(button_frame, text="⏹️ 停止录制", 
                                          command=self.stop_recording,
                                          bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"),
                                          relief="flat", padx=20, pady=8, state="disabled")
        self.stop_record_button.pack(side="left", padx=(0, 10))
        
        self.open_record_folder_button = tk.Button(button_frame, text="📁 打开录制文件夹", 
                                                 command=self.open_recording_folder,
                                                 bg="#64748b", fg="white", font=("Segoe UI", 9),
                                                 relief="flat", padx=15, pady=8)
        self.open_record_folder_button.pack(side="right")

    def create_save_card(self):
        """创建保存位置卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(content_frame, text="💾 保存位置", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(content_frame, text="选择截图保存目录", style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w", pady=(0, 10))
        
        path_frame = tk.Frame(content_frame, bg="#ffffff")
        path_frame.pack(fill="x")
        
        # 默认保存到当前文件夹下的"微信聊天记录"文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_save_path = os.path.join(os.path.dirname(current_dir), "微信聊天记录")
        self.save_path = tk.StringVar(value=default_save_path)
        path_entry = tk.Entry(path_frame, textvariable=self.save_path, font=("Segoe UI", 9), width=40)
        path_entry.pack(side="left", fill="x", expand=True)
        
        browse_button = tk.Button(path_frame, text="📁 浏览", command=self.browse_save_path,
                                 bg="#64748b", fg="white", font=("Segoe UI", 9),
                                 relief="flat", padx=15, pady=5)
        browse_button.pack(side="right", padx=(10, 0))

    def create_status_card(self):
        """创建状态显示卡片"""
        card_frame = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card_frame.pack(fill="x", pady=(0, 15), padx=5)
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        title_label = ttk.Label(content_frame, text="📊 状态信息", style='Title.TLabel')
        title_label.pack(anchor="w")
        
        status_frame = tk.Frame(content_frame, bg="#ffffff")
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_icon = tk.Label(status_frame, text="🔴", font=("Segoe UI", 12), bg="#ffffff")
        self.status_icon.pack(side="left")
        
        self.status_var = tk.StringVar(value="🔴 请先选择截图区域")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(side="left", padx=(10, 0))

    # 预览功能已删除 - 提升性能和响应速度

    def create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # 主要操作按钮
        self.start_button = tk.Button(button_frame, text="🚀 开始截图", 
                                     command=self.start_capture,
                                     bg="#10b981", fg="white", font=("Segoe UI", 12, "bold"),
                                     relief="flat", padx=30, pady=12)
        self.start_button.pack(side="left", padx=(0, 10))
        
        # 停止按钮
        self.stop_button = tk.Button(button_frame, text="⏹️ 停止", 
                                    command=self.stop_capture,
                                    bg="#ef4444", fg="white", font=("Segoe UI", 12, "bold"),
                                    relief="flat", padx=30, pady=12, state="disabled")
        self.stop_button.pack(side="left")

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

    def browse_save_path(self):
        """浏览保存路径"""
        try:
            initial_dir = self.save_path.get()
            if not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")  # 使用用户主目录作为默认
            path = filedialog.askdirectory(initialdir=initial_dir, title="选择保存位置")
            if path:
                self.save_path.set(path)
                self.status_var.set(f"✅ 保存位置已更新: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件浏览器: {str(e)}")
            self.status_var.set("❌ 文件浏览器打开失败")

    def start_capture(self):
        """开始截图"""
        if self.region_width <= 0 or self.region_height <= 0:
            messagebox.showerror("错误", "请先选择截图区域")
            return
        
        # 创建保存目录
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        self.is_capturing = True
        self.capture_count = 0
        self.capture_start_time = time.time()
        
        # 更新界面状态
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("🚀 开始截图...")
        self.status_icon.config(text="🟡")
        
        # 启动截图线程
        if self.scroll_only.get():
            threading.Thread(target=self.scroll_only_process, daemon=True).start()
        else:
            threading.Thread(target=self.capture_process, daemon=True).start()

    def capture_process(self):
        """截图处理线程"""
        try:
            interval = float(self.interval_var.get())
            scroll_mode = self.scroll_mode.get()
            scroll_direction = self.scroll_direction.get()
            region = (self.region_x, self.region_y, self.region_width, self.region_height)
            
            consecutive_errors = 0
            max_errors = 3
            
            while self.is_capturing:
                try:
                    # 截图
                    screenshot = pyautogui.screenshot(region=region)
                    
                    # 检查相似度
                    if self.auto_detect.get() and self.last_screenshot:
                        if self._fast_similarity_check(screenshot, self.last_screenshot):
                            self.root.after(0, lambda: self.status_var.set("🎯 检测到重复内容，自动停止"))
                            break
                    
                    # 保存截图
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"screenshot_{timestamp}_{self.capture_count:04d}.png"
                    filepath = os.path.join(self.save_path.get(), filename)
                    screenshot.save(filepath)
                    
                    self.capture_count += 1
                    self.last_screenshot = screenshot
                    
                    # 预览功能已删除 - 提升性能
                    
                    # 更新状态
                    elapsed = time.time() - self.capture_start_time
                    self.root.after(0, lambda: self.status_var.set(
                        f"📸 已截图 {self.capture_count} 张 | 用时 {elapsed:.1f}s"))
                    
                    # 滚动
                    if not self.scroll_controller.dynamic_scroll(scroll_direction, scroll_mode, region, self):
                        consecutive_errors += 1
                        if consecutive_errors >= max_errors:
                            self.root.after(0, lambda: self.status_var.set("❌ 连续滚动失败，自动停止"))
                            break
                    else:
                        consecutive_errors = 0
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    consecutive_errors += 1
                    self.root.after(0, lambda err=str(e): self.status_var.set(f"❌ 截图错误: {err[:30]}"))
                    if consecutive_errors >= max_errors:
                        break
                    time.sleep(1)
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.status_var.set(f"❌ 处理错误: {err[:30]}"))
        finally:
            self.root.after(0, self.stop_capture)

    def scroll_only_process(self):
        """纯滚动处理线程"""
        try:
            interval = float(self.interval_var.get())
            scroll_mode = self.scroll_mode.get()
            scroll_direction = self.scroll_direction.get()
            region = (self.region_x, self.region_y, self.region_width, self.region_height)
            
            scroll_count = 0
            consecutive_errors = 0
            max_errors = 3
            
            while self.is_capturing:
                try:
                    if self.scroll_controller.dynamic_scroll(scroll_direction, scroll_mode, region, self):
                        scroll_count += 1
                        consecutive_errors = 0
                        elapsed = time.time() - self.capture_start_time
                        self.root.after(0, lambda: self.status_var.set(
                            f"📜 已滚动 {scroll_count} 次 | 用时 {elapsed:.1f}s"))
                    else:
                        consecutive_errors += 1
                        if consecutive_errors >= max_errors:
                            self.root.after(0, lambda: self.status_var.set("❌ 连续滚动失败，自动停止"))
                            break
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    consecutive_errors += 1
                    self.root.after(0, lambda err=str(e): self.status_var.set(f"❌ 滚动错误: {err[:30]}"))
                    if consecutive_errors >= max_errors:
                        break
                    time.sleep(1)
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.status_var.set(f"❌ 处理错误: {err[:30]}"))
        finally:
            self.root.after(0, self.stop_capture)

    def _fast_similarity_check(self, img1, img2, threshold=0.001):
        """快速相似度检测"""
        try:
            # 转换为numpy数组
            arr1 = np.array(img1.convert('L'))  # 转为灰度图
            arr2 = np.array(img2.convert('L'))
            
            if arr1.shape != arr2.shape:
                return False
            
            h, w = arr1.shape
            
            # 采样策略：检查顶部、中部、底部区域
            sample_height = min(50, h // 10)
            regions = [
                (0, 0, w, sample_height),  # 顶部
                (0, h//2 - sample_height//2, w, h//2 + sample_height//2),  # 中部
                (0, h - sample_height, w, h)  # 底部
            ]
            
            total_diff = 0
            total_pixels = 0
            
            for x, y, x2, y2 in regions:
                region1 = arr1[y:y2, x:x2]
                region2 = arr2[y:y2, x:x2]
                diff = np.abs(region1.astype(int) - region2.astype(int))
                total_diff += np.sum(diff)
                total_pixels += region1.size
            
            diff_ratio = (total_diff / total_pixels) / 255.0
            return diff_ratio < threshold
            
        except Exception:
            return False

    # 预览功能已删除 - 提升性能和响应速度

    def stop_capture(self):
        """停止截图"""
        self.is_capturing = False
        self.scroll_controller.stop_flag.set()
        
        # 重置界面状态
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if self.capture_count > 0:
            elapsed = time.time() - self.capture_start_time
            self.status_var.set(f"✅ 完成！共截图 {self.capture_count} 张，用时 {elapsed:.1f}s")
            self.status_icon.config(text="🟢")
        else:
            self.status_var.set("⏹️ 已停止")
            self.status_icon.config(text="🟡")
        
        # 重置滚动控制器状态
        self.scroll_controller.page_mode_activated = False

    def start_recording(self):
        """开始屏幕录制"""
        if self.is_recording:
            messagebox.showwarning("警告", "录制已在进行中")
            return
        
        # 检查区域选择
        if self.record_region_var.get() == "selected":
            if self.region_width <= 0 or self.region_height <= 0:
                messagebox.showerror("错误", "请先选择录制区域")
                return
            record_region = (self.region_x, self.region_y, self.region_width, self.region_height)
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
        self.current_record_file = record_dir / filename
        
        # 设置录制参数
        self.recording_fps = int(self.fps_var.get())
        frame_size = (record_region[2], record_region[3])
        
        # 初始化视频写入器
        self.video_writer = cv2.VideoWriter(
            str(self.current_record_file), 
            self.recording_codec, 
            self.recording_fps, 
            frame_size
        )
        
        if not self.video_writer.isOpened():
            messagebox.showerror("错误", "无法初始化视频录制器")
            return
        
        # 开始录制
        self.is_recording = True
        self.recording_start_time = time.time()
        self.record_region = record_region
        
        # 更新UI状态
        self.start_record_button.config(state="disabled")
        self.stop_record_button.config(state="normal")
        self.record_status_var.set("🔴 正在录制...")
        
        # 启动录制线程
        self.record_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.record_thread.start()
        
        # 启动状态更新
        self._update_recording_status()
        
        messagebox.showinfo("录制开始", f"开始录制到:\n{self.current_record_file}")

    def stop_recording(self):
        """停止屏幕录制"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # 等待录制线程结束
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=3)
        
        # 释放视频写入器
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        # 计算录制时长和文件大小
        duration = time.time() - self.recording_start_time
        file_size = self.current_record_file.stat().st_size if self.current_record_file.exists() else 0
        size_mb = file_size / 1024 / 1024
        
        # 更新UI状态
        self.start_record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        self.record_status_var.set(f"✅ 录制完成 | {duration:.1f}s | {size_mb:.1f}MB")
        
        messagebox.showinfo("录制完成", 
                          f"录制已完成!\n"
                          f"文件: {self.current_record_file.name}\n"
                          f"时长: {duration:.1f}秒\n"
                          f"大小: {size_mb:.1f}MB")

    def _recording_loop(self):
        """录制循环"""
        frame_interval = 1.0 / self.recording_fps
        
        while self.is_recording:
            try:
                start_time = time.time()
                
                # 截取屏幕区域
                screenshot = pyautogui.screenshot(region=self.record_region)
                
                # 转换为OpenCV格式
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # 写入视频帧
                if self.video_writer and self.video_writer.isOpened():
                    self.video_writer.write(frame)
                
                # 控制帧率
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"录制错误: {e}")
                break

    def _update_recording_status(self):
        """更新录制状态显示"""
        if self.is_recording:
            duration = time.time() - self.recording_start_time
            self.record_status_var.set(f"🔴 录制中... | {duration:.1f}s")
            # 每秒更新一次
            self.root.after(1000, self._update_recording_status)

    def open_recording_folder(self):
        """打开录制文件夹"""
        save_dir = Path(self.save_path.get())
        record_dir = save_dir / "录制视频"
        
        if record_dir.exists():
            if os.name == 'nt':  # Windows
                os.startfile(str(record_dir))
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{record_dir}"' if sys.platform == 'darwin' else f'xdg-open "{record_dir}"')
        else:
            messagebox.showinfo("提示", "录制文件夹尚未创建")

def main():
    root = tk.Tk()
    app = ScrollScreenshotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()