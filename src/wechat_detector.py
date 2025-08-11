#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信窗口检测器 - WeChat Window Detector
自动检测微信窗口、识别聊天区域、提取界面元素
"""

import time
import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageDraw
import pywinauto
from pywinauto import Desktop, Application
from typing import Dict, List, Tuple, Optional
import threading
import tkinter as tk
from tkinter import messagebox

class WeChatDetector:
    """微信窗口检测器"""
    
    def __init__(self):
        self.wechat_window = None
        self.wechat_app = None
        self.chat_regions = {}
        self.window_info = {}
        self.detection_confidence = 0.0
        
        # 微信界面特征配置
        self.wechat_patterns = {
            'window_titles': [
                '微信', 'WeChat', 'Wechat', 
                '微信 ', ' 微信', '微信-'
            ],
            'process_names': [
                'WeChat.exe', 'wechat.exe', 'WeChatApp.exe'
            ],
            'class_names': [
                'WeChatMainWndForPC', 'ChatWnd', 'WeChatWnd'
            ]
        }
        
    def find_wechat_window(self) -> bool:
        """自动查找微信窗口"""
        try:
            # 方法1: 通过窗口标题查找
            if self._find_by_title():
                return True
                
            # 方法2: 通过进程名查找
            if self._find_by_process():
                return True
                
            # 方法3: 通过类名查找
            if self._find_by_class():
                return True
                
            return False
            
        except Exception as e:
            print(f"查找微信窗口失败: {e}")
            return False
    
    def _find_by_title(self) -> bool:
        """通过窗口标题查找微信"""
        try:
            desktop = Desktop(backend='uia')
            windows = desktop.windows()
            
            for window in windows:
                try:
                    title = window.window_text()
                    if any(pattern in title for pattern in self.wechat_patterns['window_titles']):
                        if self._validate_wechat_window(window):
                            self.wechat_window = window
                            self._extract_window_info()
                            return True
                except:
                    continue
                    
        except Exception as e:
            print(f"通过标题查找失败: {e}")
            
        return False
    
    def _find_by_process(self) -> bool:
        """通过进程名查找微信"""
        try:
            for process_name in self.wechat_patterns['process_names']:
                try:
                    app = Application(backend='uia').connect(process=process_name)
                    windows = app.windows()
                    
                    for window in windows:
                        if self._validate_wechat_window(window):
                            self.wechat_window = window
                            self.wechat_app = app
                            self._extract_window_info()
                            return True
                            
                except:
                    continue
                    
        except Exception as e:
            print(f"通过进程查找失败: {e}")
            
        return False
    
    def _find_by_class(self) -> bool:
        """通过类名查找微信"""
        try:
            desktop = Desktop(backend='uia')
            
            for class_name in self.wechat_patterns['class_names']:
                try:
                    windows = desktop.windows(class_name=class_name)
                    for window in windows:
                        if self._validate_wechat_window(window):
                            self.wechat_window = window
                            self._extract_window_info()
                            return True
                except:
                    continue
                    
        except Exception as e:
            print(f"通过类名查找失败: {e}")
            
        return False
    
    def _validate_wechat_window(self, window) -> bool:
        """验证是否为有效的微信窗口"""
        try:
            # 检查窗口是否可见
            if not window.is_visible():
                return False
                
            # 检查窗口大小（微信窗口通常较大）
            rect = window.rectangle()
            width = rect.width()
            height = rect.height()
            
            if width < 300 or height < 400:
                return False
                
            # 检查窗口标题
            title = window.window_text()
            if any(pattern in title for pattern in self.wechat_patterns['window_titles']):
                return True
                
            return False
            
        except Exception:
            return False
    
    def _extract_window_info(self):
        """提取窗口信息"""
        if not self.wechat_window:
            return
            
        try:
            rect = self.wechat_window.rectangle()
            self.window_info = {
                'title': self.wechat_window.window_text(),
                'left': rect.left,
                'top': rect.top,
                'right': rect.right,
                'bottom': rect.bottom,
                'width': rect.width(),
                'height': rect.height(),
                'center_x': rect.left + rect.width() // 2,
                'center_y': rect.top + rect.height() // 2
            }
            
        except Exception as e:
            print(f"提取窗口信息失败: {e}")
    
    def detect_chat_layout(self) -> bool:
        """检测聊天界面布局"""
        if not self.wechat_window:
            return False
            
        try:
            # 激活微信窗口
            self.wechat_window.set_focus()
            time.sleep(0.5)
            
            # 截取微信窗口
            window_screenshot = self._capture_window()
            if window_screenshot is None:
                return False
            
            # 分析界面布局
            layout_result = self._analyze_layout(window_screenshot)
            
            if layout_result:
                self.detection_confidence = layout_result.get('confidence', 0.0)
                return self.detection_confidence > 0.7
                
            return False
            
        except Exception as e:
            print(f"检测聊天布局失败: {e}")
            return False
    
    def _capture_window(self) -> Optional[Image.Image]:
        """截取微信窗口"""
        try:
            rect = self.wechat_window.rectangle()
            region = (rect.left, rect.top, rect.width(), rect.height())
            screenshot = pyautogui.screenshot(region=region)
            return screenshot
            
        except Exception as e:
            print(f"截取窗口失败: {e}")
            return None
    
    def _analyze_layout(self, screenshot: Image.Image) -> Dict:
        """分析微信界面布局"""
        try:
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            height, width = gray.shape
            
            # 基于微信界面特征进行区域划分
            regions = self._detect_interface_regions(gray, width, height)
            
            # 验证检测结果
            confidence = self._calculate_confidence(regions, width, height)
            
            if confidence > 0.7:
                self.chat_regions = regions
                return {
                    'success': True,
                    'confidence': confidence,
                    'regions': regions
                }
            
            return {'success': False, 'confidence': confidence}
            
        except Exception as e:
            print(f"分析布局失败: {e}")
            return {'success': False, 'confidence': 0.0}
    
    def _detect_interface_regions(self, gray_image, width, height) -> Dict:
        """检测界面区域"""
        regions = {}
        
        try:
            # 微信界面通常的布局比例
            # 左侧：联系人列表 (约25-30%宽度)
            # 右侧：聊天区域 (约70-75%宽度)
            
            # 检测垂直分割线（联系人列表和聊天区域的分界）
            vertical_split = self._find_vertical_split(gray_image, width, height)
            
            if vertical_split > 0:
                # 左侧区域：联系人列表
                regions['contact_list'] = {
                    'x': 0,
                    'y': 0,
                    'width': vertical_split,
                    'height': height,
                    'absolute_x': self.window_info['left'],
                    'absolute_y': self.window_info['top']
                }
                
                # 右侧区域：聊天区域
                chat_width = width - vertical_split
                regions['chat_area'] = {
                    'x': vertical_split,
                    'y': 0,
                    'width': chat_width,
                    'height': height,
                    'absolute_x': self.window_info['left'] + vertical_split,
                    'absolute_y': self.window_info['top']
                }
                
                # 进一步分析聊天区域
                chat_regions = self._analyze_chat_area(
                    gray_image[:, vertical_split:], chat_width, height, vertical_split
                )
                regions.update(chat_regions)
            
            return regions
            
        except Exception as e:
            print(f"检测界面区域失败: {e}")
            return {}
    
    def _find_vertical_split(self, gray_image, width, height) -> int:
        """查找垂直分割线"""
        try:
            # 在图像中间水平区域查找垂直线
            mid_y = height // 2
            search_height = height // 4
            
            roi = gray_image[mid_y - search_height//2:mid_y + search_height//2, :]
            
            # 计算每列的垂直梯度
            vertical_gradient = np.abs(np.diff(roi, axis=0)).sum(axis=0)
            
            # 查找梯度峰值（可能的分割线）
            # 通常在宽度的20%-40%范围内
            start_x = int(width * 0.2)
            end_x = int(width * 0.4)
            
            if start_x < end_x and end_x < len(vertical_gradient):
                search_region = vertical_gradient[start_x:end_x]
                if len(search_region) > 0:
                    max_gradient_idx = np.argmax(search_region)
                    return start_x + max_gradient_idx
            
            # 如果没有找到明显分割线，使用默认比例
            return int(width * 0.3)
            
        except Exception as e:
            print(f"查找垂直分割线失败: {e}")
            return int(width * 0.3)
    
    def _analyze_chat_area(self, chat_image, chat_width, height, offset_x) -> Dict:
        """分析聊天区域"""
        regions = {}
        
        try:
            # 聊天区域通常分为：
            # 1. 顶部：聊天对象信息栏 (约5-10%高度)
            # 2. 中间：消息列表区域 (约80-85%高度)  
            # 3. 底部：输入框区域 (约10-15%高度)
            
            # 检测水平分割线
            header_height = self._detect_header_height(chat_image, height)
            input_height = self._detect_input_height(chat_image, height)
            
            # 聊天对象信息栏
            regions['chat_header'] = {
                'x': offset_x,
                'y': 0,
                'width': chat_width,
                'height': header_height,
                'absolute_x': self.window_info['left'] + offset_x,
                'absolute_y': self.window_info['top']
            }
            
            # 消息列表区域（最重要的截图区域）
            message_y = header_height
            message_height = height - header_height - input_height
            
            regions['message_list'] = {
                'x': offset_x,
                'y': message_y,
                'width': chat_width,
                'height': message_height,
                'absolute_x': self.window_info['left'] + offset_x,
                'absolute_y': self.window_info['top'] + message_y
            }
            
            # 输入框区域
            regions['input_area'] = {
                'x': offset_x,
                'y': height - input_height,
                'width': chat_width,
                'height': input_height,
                'absolute_x': self.window_info['left'] + offset_x,
                'absolute_y': self.window_info['top'] + height - input_height
            }
            
            return regions
            
        except Exception as e:
            print(f"分析聊天区域失败: {e}")
            return {}
    
    def _detect_header_height(self, chat_image, total_height) -> int:
        """检测头部高度"""
        try:
            # 通常头部占总高度的5-10%
            estimated_height = int(total_height * 0.08)
            
            # 在估计区域附近查找水平分割线
            search_start = max(int(total_height * 0.05), 20)
            search_end = min(int(total_height * 0.15), estimated_height + 20)
            
            if search_start < search_end and search_end < chat_image.shape[0]:
                roi = chat_image[search_start:search_end, :]
                horizontal_gradient = np.abs(np.diff(roi, axis=1)).sum(axis=1)
                
                if len(horizontal_gradient) > 0:
                    max_gradient_idx = np.argmax(horizontal_gradient)
                    return search_start + max_gradient_idx
            
            return estimated_height
            
        except Exception:
            return int(total_height * 0.08)
    
    def _detect_input_height(self, chat_image, total_height) -> int:
        """检测输入框高度"""
        try:
            # 通常输入框占总高度的10-15%
            estimated_height = int(total_height * 0.12)
            
            # 从底部向上查找
            search_start = max(int(total_height * 0.8), total_height - 100)
            search_end = total_height - 10
            
            if search_start < search_end and search_start >= 0:
                roi = chat_image[search_start:search_end, :]
                horizontal_gradient = np.abs(np.diff(roi, axis=1)).sum(axis=1)
                
                if len(horizontal_gradient) > 0:
                    # 从底部开始查找第一个明显的分割线
                    for i in range(len(horizontal_gradient) - 1, -1, -1):
                        if horizontal_gradient[i] > np.mean(horizontal_gradient) * 1.5:
                            return total_height - (search_start + i)
            
            return estimated_height
            
        except Exception:
            return int(total_height * 0.12)
    
    def _calculate_confidence(self, regions, width, height) -> float:
        """计算检测置信度"""
        try:
            confidence = 0.0
            
            # 检查是否检测到基本区域
            required_regions = ['contact_list', 'chat_area', 'message_list']
            detected_regions = sum(1 for region in required_regions if region in regions)
            confidence += (detected_regions / len(required_regions)) * 0.4
            
            # 检查区域比例是否合理
            if 'contact_list' in regions and 'chat_area' in regions:
                contact_ratio = regions['contact_list']['width'] / width
                chat_ratio = regions['chat_area']['width'] / width
                
                # 理想比例：联系人列表25-35%，聊天区域65-75%
                if 0.2 <= contact_ratio <= 0.4 and 0.6 <= chat_ratio <= 0.8:
                    confidence += 0.3
                elif 0.15 <= contact_ratio <= 0.45 and 0.55 <= chat_ratio <= 0.85:
                    confidence += 0.2
            
            # 检查消息列表区域是否合理
            if 'message_list' in regions:
                msg_region = regions['message_list']
                msg_ratio = msg_region['height'] / height
                
                # 消息列表应该占大部分高度
                if 0.6 <= msg_ratio <= 0.85:
                    confidence += 0.3
                elif 0.5 <= msg_ratio <= 0.9:
                    confidence += 0.2
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.0
    
    def get_optimal_capture_region(self) -> Optional[Tuple[int, int, int, int]]:
        """获取最佳截图区域（消息列表区域）"""
        if 'message_list' not in self.chat_regions:
            return None
            
        region = self.chat_regions['message_list']
        return (
            region['absolute_x'],
            region['absolute_y'], 
            region['width'],
            region['height']
        )
    
    def get_all_regions(self) -> Dict:
        """获取所有检测到的区域"""
        return self.chat_regions.copy()
    
    def get_window_info(self) -> Dict:
        """获取窗口信息"""
        return self.window_info.copy()
    
    def activate_wechat_window(self) -> bool:
        """激活微信窗口"""
        if not self.wechat_window:
            return False
            
        try:
            self.wechat_window.set_focus()
            time.sleep(0.2)
            return True
        except Exception as e:
            print(f"激活窗口失败: {e}")
            return False
    
    def is_wechat_active(self) -> bool:
        """检查微信窗口是否处于活动状态"""
        if not self.wechat_window:
            return False
            
        try:
            return self.wechat_window.has_focus()
        except Exception:
            return False
    
    def extract_message_info(self, screenshot: Image.Image) -> Dict:
        """提取消息信息（为OCR功能预留接口）"""
        # 这里可以集成OCR功能来提取文字信息
        # 目前返回基本的图像信息
        return {
            'image_size': screenshot.size,
            'timestamp': time.time(),
            'has_text': True,  # 可以通过图像分析判断
            'message_count': 0  # 可以通过图像分析估算
        }
    
    def create_detection_visualization(self) -> Optional[Image.Image]:
        """创建检测结果可视化图像"""
        if not self.wechat_window or not self.chat_regions:
            return None
            
        try:
            # 截取当前窗口
            screenshot = self._capture_window()
            if screenshot is None:
                return None
            
            # 在截图上绘制检测区域
            draw = ImageDraw.Draw(screenshot)
            
            colors = {
                'contact_list': 'red',
                'chat_header': 'blue', 
                'message_list': 'green',
                'input_area': 'orange'
            }
            
            for region_name, region in self.chat_regions.items():
                if region_name in colors:
                    x, y = region['x'], region['y']
                    w, h = region['width'], region['height']
                    
                    # 绘制矩形框
                    draw.rectangle([x, y, x + w, y + h], 
                                 outline=colors[region_name], width=3)
                    
                    # 添加标签
                    draw.text((x + 5, y + 5), region_name, 
                            fill=colors[region_name])
            
            return screenshot
            
        except Exception as e:
            print(f"创建可视化失败: {e}")
            return None


# 测试和使用示例
if __name__ == "__main__":
    detector = WeChatDetector()
    
    print("🔍 开始检测微信窗口...")
    if detector.find_wechat_window():
        print("✅ 找到微信窗口")
        print(f"窗口信息: {detector.get_window_info()}")
        
        print("\n🔍 开始分析聊天布局...")
        if detector.detect_chat_layout():
            print(f"✅ 布局分析完成，置信度: {detector.detection_confidence:.2f}")
            print(f"检测到的区域: {list(detector.get_all_regions().keys())}")
            
            # 获取最佳截图区域
            capture_region = detector.get_optimal_capture_region()
            if capture_region:
                print(f"📸 推荐截图区域: {capture_region}")
            
            # 创建可视化图像
            viz_image = detector.create_detection_visualization()
            if viz_image:
                viz_image.save("wechat_detection_result.png")
                print("💾 检测结果已保存为 wechat_detection_result.png")
        else:
            print("❌ 布局分析失败")
    else:
        print("❌ 未找到微信窗口")