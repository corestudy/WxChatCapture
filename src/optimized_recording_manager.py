#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的录屏管理器 - 提供高性能视频录制功能
"""

import time
import threading
import cv2
import numpy as np
import pyautogui
from PIL import Image
from queue import Queue, Empty
from pathlib import Path
from typing import Optional, Tuple, Callable
import psutil
import os


class OptimizedRecordingManager:
    """优化的录屏管理器"""
    
    def __init__(self, fps: int = 10, codec: str = 'mp4v'):
        self.fps = fps
        self.codec = cv2.VideoWriter_fourcc(*codec)
        self.is_recording = False
        self.video_writer = None
        self.record_thread = None
        
        # 性能优化配置
        self.frame_buffer = []
        self.buffer_size = self._calculate_optimal_buffer_size()
        self.frame_skip_threshold = 1.5  # 如果处理时间超过目标时间的1.5倍则跳帧
        self.target_frame_time = 1.0 / fps
        
        # 统计信息
        self.stats = {
            'frames_recorded': 0,
            'frames_skipped': 0,
            'total_recording_time': 0,
            'buffer_flushes': 0,
            'average_frame_time': 0
        }
        
        # 性能监控
        self.frame_times = []
        self.max_frame_time_samples = 100
        
        print(f"🎥 录屏管理器初始化: FPS={fps}, 缓冲区={self.buffer_size}帧")
    
    def _calculate_optimal_buffer_size(self) -> int:
        """根据系统性能计算最优缓冲区大小"""
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = os.cpu_count()
        
        # 基于内存和CPU核心数计算缓冲区大小
        if memory_gb >= 8 and cpu_count >= 8:
            return 60  # 高性能系统
        elif memory_gb >= 4 and cpu_count >= 4:
            return 30  # 中等性能系统
        else:
            return 15  # 低性能系统
    
    def start_recording(self, region: Tuple[int, int, int, int], output_path: str) -> bool:
        """开始录制"""
        if self.is_recording:
            print("⚠️ 录制已在进行中")
            return False
        
        try:
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 计算帧大小
            frame_size = (region[2], region[3])
            
            # 初始化视频写入器
            self.video_writer = cv2.VideoWriter(
                output_path, 
                self.codec, 
                self.fps, 
                frame_size
            )
            
            if not self.video_writer.isOpened():
                print("❌ 无法初始化视频写入器")
                return False
            
            # 设置录制参数
            self.is_recording = True
            self.record_region = region
            self.output_path = output_path
            self.recording_start_time = time.time()
            
            # 重置统计信息
            self._reset_stats()
            
            # 启动录制线程
            self.record_thread = threading.Thread(
                target=self._optimized_recording_loop, 
                daemon=True
            )
            self.record_thread.start()
            
            print(f"✅ 开始录制: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 启动录制失败: {e}")
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            return False
    
    def stop_recording(self) -> dict:
        """停止录制并返回统计信息"""
        if not self.is_recording:
            print("⚠️ 当前没有进行录制")
            return {}
        
        self.is_recording = False
        
        # 等待录制线程结束
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=5)
        
        # 写入剩余的缓冲帧
        if self.frame_buffer:
            self._flush_frame_buffer()
        
        # 释放视频写入器
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        # 计算最终统计信息
        total_time = time.time() - self.recording_start_time
        self.stats['total_recording_time'] = total_time
        
        if self.frame_times:
            self.stats['average_frame_time'] = sum(self.frame_times) / len(self.frame_times)
        
        # 获取文件信息
        file_stats = self._get_file_stats()
        
        print(f"✅ 录制完成: {self.output_path}")
        self._print_recording_stats(file_stats)
        
        return {**self.stats, **file_stats}
    
    def _optimized_recording_loop(self):
        """优化的录制循环"""
        consecutive_errors = 0
        max_errors = 5
        
        while self.is_recording:
            frame_start_time = time.time()
            
            try:
                # 捕获屏幕帧
                screenshot = pyautogui.screenshot(region=self.record_region)
                
                # 转换为OpenCV格式
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # 添加到缓冲区
                self.frame_buffer.append(frame)
                self.stats['frames_recorded'] += 1
                
                # 检查是否需要刷新缓冲区
                if len(self.frame_buffer) >= self.buffer_size:
                    self._flush_frame_buffer()
                
                # 计算帧处理时间
                frame_processing_time = time.time() - frame_start_time
                self._update_frame_time_stats(frame_processing_time)
                
                # 动态帧率控制
                sleep_time = self._calculate_sleep_time(frame_processing_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                elif frame_processing_time > self.target_frame_time * self.frame_skip_threshold:
                    # 如果处理时间过长，跳过下一帧以保持帧率
                    self.stats['frames_skipped'] += 1
                
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                print(f"⚠️ 录制帧错误: {e}")
                
                if consecutive_errors >= max_errors:
                    print("❌ 连续错误过多，停止录制")
                    break
                
                time.sleep(0.1)
    
    def _flush_frame_buffer(self):
        """刷新帧缓冲区到视频文件"""
        if not self.frame_buffer or not self.video_writer:
            return
        
        try:
            for frame in self.frame_buffer:
                if self.video_writer.isOpened():
                    self.video_writer.write(frame)
            
            self.frame_buffer.clear()
            self.stats['buffer_flushes'] += 1
            
        except Exception as e:
            print(f"⚠️ 刷新缓冲区错误: {e}")
    
    def _update_frame_time_stats(self, frame_time: float):
        """更新帧时间统计"""
        self.frame_times.append(frame_time)
        
        # 限制样本数量以避免内存泄漏
        if len(self.frame_times) > self.max_frame_time_samples:
            self.frame_times.pop(0)
    
    def _calculate_sleep_time(self, frame_processing_time: float) -> float:
        """计算睡眠时间以维持目标帧率"""
        return max(0, self.target_frame_time - frame_processing_time)
    
    def _reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'frames_recorded': 0,
            'frames_skipped': 0,
            'total_recording_time': 0,
            'buffer_flushes': 0,
            'average_frame_time': 0
        }
        self.frame_times.clear()
    
    def _get_file_stats(self) -> dict:
        """获取录制文件统计信息"""
        try:
            if Path(self.output_path).exists():
                file_size = Path(self.output_path).stat().st_size
                return {
                    'file_size_mb': file_size / (1024 * 1024),
                    'file_exists': True,
                    'output_path': self.output_path
                }
            else:
                return {
                    'file_size_mb': 0,
                    'file_exists': False,
                    'output_path': self.output_path
                }
        except Exception as e:
            print(f"⚠️ 获取文件统计失败: {e}")
            return {'file_size_mb': 0, 'file_exists': False}
    
    def _print_recording_stats(self, file_stats: dict):
        """打印录制统计信息"""
        print(f"📊 录制统计:")
        print(f"   录制时长: {self.stats['total_recording_time']:.1f}秒")
        print(f"   录制帧数: {self.stats['frames_recorded']}")
        print(f"   跳过帧数: {self.stats['frames_skipped']}")
        print(f"   缓冲刷新: {self.stats['buffer_flushes']}次")
        print(f"   平均帧时间: {self.stats['average_frame_time']*1000:.1f}ms")
        print(f"   文件大小: {file_stats['file_size_mb']:.1f}MB")
        
        if self.stats['frames_recorded'] > 0:
            actual_fps = self.stats['frames_recorded'] / self.stats['total_recording_time']
            print(f"   实际帧率: {actual_fps:.1f} FPS")
    
    def get_current_stats(self) -> dict:
        """获取当前录制统计信息"""
        if not self.is_recording:
            return self.stats
        
        current_time = time.time() - self.recording_start_time
        current_fps = self.stats['frames_recorded'] / max(current_time, 0.1)
        
        return {
            **self.stats,
            'current_recording_time': current_time,
            'current_fps': current_fps,
            'buffer_level': len(self.frame_buffer),
            'is_recording': self.is_recording
        }
    
    def adjust_quality_settings(self, cpu_usage_percent: float):
        """根据CPU使用率动态调整质量设置"""
        if cpu_usage_percent > 80:
            # 高CPU使用率 - 降低质量
            self.buffer_size = max(10, self.buffer_size - 5)
            self.frame_skip_threshold = 1.2
            print(f"🔧 降低录制质量: 缓冲区={self.buffer_size}")
        elif cpu_usage_percent < 50:
            # 低CPU使用率 - 提高质量
            max_buffer = self._calculate_optimal_buffer_size()
            self.buffer_size = min(max_buffer, self.buffer_size + 5)
            self.frame_skip_threshold = 1.5
            print(f"🔧 提高录制质量: 缓冲区={self.buffer_size}")
    
    def cleanup(self):
        """清理资源"""
        if self.is_recording:
            self.stop_recording()
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        self.frame_buffer.clear()
        self.frame_times.clear()
        
        print("✅ 录屏管理器资源清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()


class AdaptiveRecordingManager(OptimizedRecordingManager):
    """自适应录屏管理器 - 根据系统性能自动调整参数"""
    
    def __init__(self, fps: int = 10, codec: str = 'mp4v'):
        super().__init__(fps, codec)
        self.performance_monitor = None
        self.last_adjustment_time = 0
        self.adjustment_interval = 5.0  # 每5秒检查一次性能
    
    def start_recording(self, region: Tuple[int, int, int, int], output_path: str) -> bool:
        """开始自适应录制"""
        success = super().start_recording(region, output_path)
        
        if success:
            # 启动性能监控
            self._start_performance_monitoring()
        
        return success
    
    def _start_performance_monitoring(self):
        """启动性能监控线程"""
        def monitor_performance():
            while self.is_recording:
                try:
                    current_time = time.time()
                    
                    # 检查是否需要调整
                    if current_time - self.last_adjustment_time >= self.adjustment_interval:
                        cpu_percent = psutil.cpu_percent(interval=1)
                        memory_percent = psutil.virtual_memory().percent
                        
                        # 根据系统负载调整设置
                        self._adaptive_adjustment(cpu_percent, memory_percent)
                        self.last_adjustment_time = current_time
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️ 性能监控错误: {e}")
                    break
        
        self.performance_monitor = threading.Thread(target=monitor_performance, daemon=True)
        self.performance_monitor.start()
    
    def _adaptive_adjustment(self, cpu_percent: float, memory_percent: float):
        """自适应调整录制参数"""
        # CPU负载调整
        if cpu_percent > 85:
            self.adjust_quality_settings(cpu_percent)
        
        # 内存使用调整
        if memory_percent > 90:
            # 减少缓冲区大小以降低内存使用
            self.buffer_size = max(5, self.buffer_size // 2)
            print(f"🔧 内存压力调整: 缓冲区={self.buffer_size}")


# 使用示例
if __name__ == "__main__":
    # 创建自适应录屏管理器
    recorder = AdaptiveRecordingManager(fps=15)
    
    try:
        # 开始录制
        region = (100, 100, 800, 600)
        output_path = "test_optimized_recording.mp4"
        
        if recorder.start_recording(region, output_path):
            print("✅ 录制已开始，按Enter停止...")
            input()  # 等待用户输入
            
            # 停止录制
            stats = recorder.stop_recording()
            print(f"📊 最终统计: {stats}")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断录制")
    finally:
        recorder.cleanup()