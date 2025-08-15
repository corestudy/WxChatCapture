#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能滚动截图工具 v3.0 - 工具函数模块

提供项目中使用的通用工具函数和辅助类。

作者: 智能截图工具开发团队
版本: 3.0.6
许可: MIT 许可证
"""

# 标准库导入
import os
import sys
import time
import logging
from typing import Optional, Tuple, Union, Any
from pathlib import Path

# 第三方库导入
import tkinter as tk
from tkinter import messagebox

# 项目配置
__version__ = "3.0.6"
__author__ = "智能截图工具开发团队"


class Logger:
    """日志管理类"""
    
    def __init__(self, name: str = "smart_screenshot", level: int = logging.INFO):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # 创建文件处理器
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(
                log_dir / f"{name}_{time.strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str) -> None:
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """记录调试日志"""
        self.logger.debug(message)


class PathValidator:
    """路径验证工具类"""
    
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """
        验证路径是否有效
        
        Args:
            path: 要验证的路径
            
        Returns:
            bool: 路径是否有效
        """
        try:
            Path(path).resolve()
            return True
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """
        确保目录存在，不存在则创建
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 是否成功
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        获取安全的文件名（移除非法字符）
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 安全的文件名
        """
        # Windows文件名非法字符
        illegal_chars = '<>:"/\\|?*'
        safe_filename = filename
        
        for char in illegal_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 移除前后空格和点
        safe_filename = safe_filename.strip(' .')
        
        # 确保不为空
        if not safe_filename:
            safe_filename = "unnamed_file"
        
        return safe_filename


class UIHelper:
    """UI辅助工具类"""
    
    @staticmethod
    def center_window(window: tk.Tk, width: int, height: int) -> None:
        """
        将窗口居中显示
        
        Args:
            window: tkinter窗口对象
            width: 窗口宽度
            height: 窗口高度
        """
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置和大小
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def show_error(title: str, message: str) -> None:
        """
        显示错误对话框
        
        Args:
            title: 对话框标题
            message: 错误信息
        """
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_info(title: str, message: str) -> None:
        """
        显示信息对话框
        
        Args:
            title: 对话框标题
            message: 信息内容
        """
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str) -> None:
        """
        显示警告对话框
        
        Args:
            title: 对话框标题
            message: 警告信息
        """
        messagebox.showwarning(title, message)
    
    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """
        显示是/否确认对话框
        
        Args:
            title: 对话框标题
            message: 确认信息
            
        Returns:
            bool: 用户选择结果
        """
        return messagebox.askyesno(title, message)


class PerformanceMonitor:
    """性能监控工具类"""
    
    def __init__(self):
        """初始化性能监控器"""
        self.start_time: Optional[float] = None
        self.checkpoints: list = []
    
    def start(self) -> None:
        """开始监控"""
        self.start_time = time.time()
        self.checkpoints.clear()
    
    def checkpoint(self, name: str) -> float:
        """
        添加检查点
        
        Args:
            name: 检查点名称
            
        Returns:
            float: 从开始到现在的时间
        """
        if self.start_time is None:
            raise RuntimeError("请先调用start()方法")
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        self.checkpoints.append({
            'name': name,
            'time': current_time,
            'elapsed': elapsed
        })
        
        return elapsed
    
    def get_report(self) -> str:
        """
        获取性能报告
        
        Returns:
            str: 性能报告字符串
        """
        if not self.checkpoints:
            return "无性能数据"
        
        report = "性能监控报告:\n"
        report += "=" * 40 + "\n"
        
        for i, checkpoint in enumerate(self.checkpoints):
            if i == 0:
                interval = checkpoint['elapsed']
            else:
                interval = checkpoint['elapsed'] - self.checkpoints[i-1]['elapsed']
            
            report += f"{checkpoint['name']}: {checkpoint['elapsed']:.3f}s (+{interval:.3f}s)\n"
        
        total_time = self.checkpoints[-1]['elapsed']
        report += "=" * 40 + "\n"
        report += f"总耗时: {total_time:.3f}s"
        
        return report


# 全局日志器实例
logger = Logger()

# 导出的公共API
__all__ = [
    'Logger',
    'PathValidator', 
    'UIHelper',
    'PerformanceMonitor',
    'logger'
]