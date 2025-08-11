#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的截图管理器 - 提供高性能截图和相似度检测功能
"""

import time
import threading
import hashlib
import numpy as np
from PIL import Image
import pyautogui
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, Callable
import psutil
import os


class OptimizedScreenshotManager:
    """优化的截图管理器"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.screenshot_queue = Queue(maxsize=10)
        self.save_queue = Queue(maxsize=20)
        self.similarity_queue = Queue(maxsize=5)
        
        # 性能配置
        self.performance_config = self._auto_configure_performance()
        
        # 缓存和状态
        self.last_screenshot_hash = None
        self.screenshot_cache = {}
        self.cache_size_limit = 50
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # 统计信息
        self.stats = {
            'screenshots_taken': 0,
            'duplicates_detected': 0,
            'total_processing_time': 0,
            'memory_usage': 0
        }
    
    def _auto_configure_performance(self) -> dict:
        """根据系统性能自动配置参数"""
        cpu_count = os.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        config = {
            'use_histogram_similarity': memory_gb >= 4,
            'compression_level': 6 if memory_gb >= 8 else 9,
            'max_cache_size': min(100, int(memory_gb * 10)),
            'similarity_threshold': 0.95,
            'hash_similarity_threshold': 0.001,
            'enable_parallel_processing': cpu_count >= 4
        }
        
        print(f"🔧 性能配置: CPU={cpu_count}核, RAM={memory_gb:.1f}GB")
        print(f"   - 并行处理: {'启用' if config['enable_parallel_processing'] else '禁用'}")
        print(f"   - 缓存大小: {config['max_cache_size']}")
        print(f"   - 压缩级别: {config['compression_level']}")
        
        return config
    
    def capture_screenshot_optimized(self, region: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        """优化的截图捕获"""
        start_time = time.time()
        
        try:
            # 使用重试机制
            screenshot = self._capture_with_retry(region)
            
            if screenshot:
                self.stats['screenshots_taken'] += 1
                processing_time = time.time() - start_time
                self.stats['total_processing_time'] += processing_time
                
                return screenshot
                
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def _capture_with_retry(self, region: Tuple[int, int, int, int], max_retries: int = 3) -> Optional[Image.Image]:
        """带重试机制的截图捕获"""
        for attempt in range(max_retries):
            try:
                screenshot = pyautogui.screenshot(region=region)
                return screenshot
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(0.1 * (attempt + 1))  # 指数退避
        return None
    
    def fast_similarity_check(self, img1: Image.Image, img2: Image.Image) -> bool:
        """优化的快速相似度检测"""
        if not img1 or not img2:
            return False
        
        try:
            # 方法1: 快速哈希比较（用于完全相同的图像）
            hash1 = self._get_image_hash(img1)
            hash2 = self._get_image_hash(img2)
            
            if hash1 == hash2:
                self.stats['duplicates_detected'] += 1
                return True
            
            # 方法2: 直方图比较（用于相似图像）
            if self.performance_config['use_histogram_similarity']:
                return self._histogram_similarity(img1, img2)
            else:
                return self._sampling_similarity(img1, img2)
                
        except Exception as e:
            print(f"⚠️ 相似度检测错误: {e}")
            return False
    
    def _get_image_hash(self, image: Image.Image) -> str:
        """获取图像哈希值"""
        # 使用缓存避免重复计算
        image_id = id(image)
        if image_id in self.screenshot_cache:
            return self.screenshot_cache[image_id]
        
        # 计算哈希
        image_bytes = image.tobytes()
        hash_value = hashlib.md5(image_bytes).hexdigest()
        
        # 缓存管理
        if len(self.screenshot_cache) >= self.cache_size_limit:
            # 删除最旧的缓存项
            oldest_key = next(iter(self.screenshot_cache))
            del self.screenshot_cache[oldest_key]
        
        self.screenshot_cache[image_id] = hash_value
        return hash_value
    
    def _histogram_similarity(self, img1: Image.Image, img2: Image.Image) -> bool:
        """基于直方图的相似度检测"""
        try:
            # 转换为灰度图像
            gray1 = img1.convert('L')
            gray2 = img2.convert('L')
            
            # 计算直方图
            hist1 = np.array(gray1.histogram())
            hist2 = np.array(gray2.histogram())
            
            # 计算相关系数
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            
            # 处理NaN值
            if np.isnan(correlation):
                correlation = 0
            
            is_similar = correlation > self.performance_config['similarity_threshold']
            if is_similar:
                self.stats['duplicates_detected'] += 1
            
            return is_similar
            
        except Exception as e:
            print(f"⚠️ 直方图相似度检测错误: {e}")
            return False
    
    def _sampling_similarity(self, img1: Image.Image, img2: Image.Image) -> bool:
        """基于采样的相似度检测（低内存版本）"""
        try:
            # 缩小图像进行快速比较
            size = (64, 64)
            small1 = img1.resize(size, Image.Resampling.LANCZOS).convert('L')
            small2 = img2.resize(size, Image.Resampling.LANCZOS).convert('L')
            
            # 转换为numpy数组
            arr1 = np.array(small1)
            arr2 = np.array(small2)
            
            # 计算均方误差
            mse = np.mean((arr1 - arr2) ** 2)
            
            # 相似度阈值（MSE越小越相似）
            threshold = 100  # 可调整
            is_similar = mse < threshold
            
            if is_similar:
                self.stats['duplicates_detected'] += 1
            
            return is_similar
            
        except Exception as e:
            print(f"⚠️ 采样相似度检测错误: {e}")
            return False
    
    def save_screenshot_async(self, screenshot: Image.Image, filepath: str, callback: Optional[Callable] = None):
        """异步保存截图"""
        def save_task():
            try:
                # 优化的保存参数
                save_kwargs = {
                    'optimize': True,
                    'compress_level': self.performance_config['compression_level']
                }
                
                screenshot.save(filepath, 'PNG', **save_kwargs)
                
                if callback:
                    callback(filepath, True)
                    
            except Exception as e:
                print(f"❌ 保存截图失败: {e}")
                if callback:
                    callback(filepath, False)
        
        # 提交到线程池
        self.executor.submit(save_task)
    
    def batch_save_screenshots(self, screenshots_and_paths: list, callback: Optional[Callable] = None):
        """批量保存截图"""
        def batch_save_task():
            success_count = 0
            total_count = len(screenshots_and_paths)
            
            for screenshot, filepath in screenshots_and_paths:
                try:
                    save_kwargs = {
                        'optimize': True,
                        'compress_level': self.performance_config['compression_level']
                    }
                    screenshot.save(filepath, 'PNG', **save_kwargs)
                    success_count += 1
                except Exception as e:
                    print(f"❌ 批量保存失败 {filepath}: {e}")
            
            if callback:
                callback(success_count, total_count)
        
        self.executor.submit(batch_save_task)
    
    def get_performance_stats(self) -> dict:
        """获取性能统计信息"""
        current_memory = psutil.Process().memory_info().rss / (1024**2)  # MB
        
        avg_processing_time = (
            self.stats['total_processing_time'] / max(1, self.stats['screenshots_taken'])
        )
        
        return {
            'screenshots_taken': self.stats['screenshots_taken'],
            'duplicates_detected': self.stats['duplicates_detected'],
            'duplicate_rate': self.stats['duplicates_detected'] / max(1, self.stats['screenshots_taken']),
            'avg_processing_time': avg_processing_time,
            'current_memory_mb': current_memory,
            'cache_size': len(self.screenshot_cache)
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.executor.shutdown(wait=True, timeout=5)
            self.screenshot_cache.clear()
            
            # 清空队列
            while not self.screenshot_queue.empty():
                try:
                    self.screenshot_queue.get_nowait()
                except Empty:
                    break
            
            while not self.save_queue.empty():
                try:
                    self.save_queue.get_nowait()
                except Empty:
                    break
                    
            print("✅ 截图管理器资源清理完成")
            
        except Exception as e:
            print(f"⚠️ 资源清理警告: {e}")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        
    def get_current_stats(self) -> dict:
        """获取当前性能统计"""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        
        return {
            'runtime_seconds': current_time - self.start_time,
            'memory_usage_mb': current_memory / (1024**2),
            'memory_delta_mb': (current_memory - self.start_memory) / (1024**2),
            'cpu_percent': psutil.Process().cpu_percent()
        }
    
    def print_stats(self):
        """打印性能统计"""
        stats = self.get_current_stats()
        print(f"📊 性能统计:")
        print(f"   运行时间: {stats['runtime_seconds']:.1f}秒")
        print(f"   内存使用: {stats['memory_usage_mb']:.1f}MB")
        print(f"   内存变化: {stats['memory_delta_mb']:+.1f}MB")
        print(f"   CPU使用率: {stats['cpu_percent']:.1f}%")


# 使用示例
if __name__ == "__main__":
    # 创建优化的截图管理器
    manager = OptimizedScreenshotManager()
    monitor = PerformanceMonitor()
    
    try:
        # 测试截图
        region = (100, 100, 800, 600)
        screenshot = manager.capture_screenshot_optimized(region)
        
        if screenshot:
            print("✅ 截图成功")
            
            # 异步保存
            manager.save_screenshot_async(
                screenshot, 
                "test_optimized.png",
                lambda path, success: print(f"保存{'成功' if success else '失败'}: {path}")
            )
            
            # 等待保存完成
            time.sleep(1)
            
            # 显示统计信息
            stats = manager.get_performance_stats()
            print(f"📊 截图统计: {stats}")
            
            monitor.print_stats()
        
    finally:
        manager.cleanup()