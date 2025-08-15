#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级截图管理器 - 实现异步截图管道和智能优化
版本: 3.0.6
"""

import time
import threading
import asyncio
import hashlib
import numpy as np
from PIL import Image
import pyautogui
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple, Callable, List
import psutil
import os
from dataclasses import dataclass
from collections import deque
import weakref
import cv2


@dataclass
class ScreenshotTask:
    """截图任务数据类"""
    region: Tuple[int, int, int, int]
    timestamp: float
    task_id: int
    priority: int = 0


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    avg_capture_time: float = 0.0
    avg_similarity_time: float = 0.0
    avg_save_time: float = 0.0
    memory_usage_mb: float = 0.0
    cache_hit_rate: float = 0.0
    throughput_fps: float = 0.0


class SmartCache:
    """智能缓存管理器"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = deque()
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key):
        """获取缓存项"""
        if key in self.cache:
            self.hit_count += 1
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        else:
            self.miss_count += 1
            return None
    
    def put(self, key, value):
        """添加缓存项"""
        if key in self.cache:
            # 更新现有项
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # 删除最久未使用的项
            oldest_key = self.access_order.popleft()
            del self.cache[oldest_key]
        
        self.cache[key] = value
        self.access_order.append(key)
    
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()
        self.hit_count = 0
        self.miss_count = 0


class AdaptiveWaitManager:
    """自适应等待管理器"""
    
    def __init__(self):
        self.wait_times = deque(maxlen=10)  # 保留最近10次的等待时间
        self.base_wait = 0.3
        self.min_wait = 0.1
        self.max_wait = 2.0
    
    def calculate_wait_time(self, scroll_mode: str, system_load: float) -> float:
        """计算自适应等待时间"""
        # 基础等待时间
        if scroll_mode == "page":
            base = 0.5
        else:  # mouse
            base = 0.3
        
        # 根据系统负载调整
        load_factor = 1.0 + (system_load / 100.0) * 0.5
        
        # 根据历史性能调整
        if len(self.wait_times) >= 3:
            avg_wait = sum(self.wait_times) / len(self.wait_times)
            # 如果平均等待时间过长，适当减少
            if avg_wait > base * 1.5:
                base *= 0.9
            elif avg_wait < base * 0.5:
                base *= 1.1
        
        wait_time = base * load_factor
        wait_time = max(self.min_wait, min(self.max_wait, wait_time))
        
        self.wait_times.append(wait_time)
        return wait_time


class AdvancedScreenshotManager:
    """高级截图管理器 - 实现异步管道和智能优化"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        
        # 任务队列
        self.capture_queue = Queue(maxsize=20)
        self.similarity_queue = Queue(maxsize=10)
        self.save_queue = Queue(maxsize=50)
        
        # 线程池
        self.capture_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="capture")
        self.similarity_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="similarity")
        self.save_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="save")
        
        # 智能缓存
        self.image_cache = SmartCache(max_size=50)
        self.hash_cache = SmartCache(max_size=100)
        
        # 自适应管理器
        self.wait_manager = AdaptiveWaitManager()
        
        # 性能配置
        self.performance_config = self._auto_configure_performance()
        
        # 统计信息
        self.metrics = PerformanceMetrics()
        self.stats = {
            'screenshots_taken': 0,
            'duplicates_detected': 0,
            'total_processing_time': 0,
            'memory_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # 运行状态
        self.is_running = False
        self.task_counter = 0
        self.save_directory = "screenshots"  # 默认保存目录
        
        # 启动后台处理线程
        self._start_background_processors()
    
    def set_save_directory(self, path: str):
        """设置截图保存目录"""
        self.save_directory = path
        print(f"💾 截图保存目录已设置为: {path}")
    
    def _auto_configure_performance(self) -> dict:
        """自动配置性能参数"""
        cpu_count = os.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        config = {
            'use_advanced_similarity': memory_gb >= 8,
            'compression_level': 6 if memory_gb >= 8 else 9,
            'max_cache_size': min(100, int(memory_gb * 10)),
            'similarity_threshold': 0.95,
            'hash_similarity_threshold': 0.001,
            'enable_parallel_processing': cpu_count >= 4,
            'batch_save_size': min(10, max(3, cpu_count)),
            'adaptive_quality': True,
            'memory_limit_mb': int(memory_gb * 1024 * 0.3)  # 使用30%内存
        }
        
        print(f"🔧 高级性能配置: CPU={cpu_count}核, RAM={memory_gb:.1f}GB")
        print(f"   - 高级相似度: {'启用' if config['use_advanced_similarity'] else '禁用'}")
        print(f"   - 批量保存: {config['batch_save_size']}张/批")
        print(f"   - 内存限制: {config['memory_limit_mb']}MB")
        
        return config
    
    def _start_background_processors(self):
        """启动后台处理线程"""
        self.is_running = True
        
        # 相似度检测处理器
        threading.Thread(target=self._similarity_processor, daemon=True, name="similarity_processor").start()
        
        # 批量保存处理器
        threading.Thread(target=self._batch_save_processor, daemon=True, name="batch_save_processor").start()
        
        # 性能监控器
        threading.Thread(target=self._performance_monitor, daemon=True, name="performance_monitor").start()
    
    def capture_screenshot_async(self, region: Tuple[int, int, int, int], 
                                callback: Optional[Callable] = None) -> int:
        """异步截图捕获"""
        task_id = self.task_counter
        self.task_counter += 1
        
        task = ScreenshotTask(
            region=region,
            timestamp=time.time(),
            task_id=task_id
        )
        
        # 提交到捕获队列
        future = self.capture_executor.submit(self._capture_task, task, callback)
        return task_id
    
    def _capture_task(self, task: ScreenshotTask, callback: Optional[Callable] = None):
        """执行截图任务"""
        start_time = time.time()
        
        try:
            # 检查缓存
            cache_key = f"{task.region}_{int(task.timestamp)}"
            cached_screenshot = self.image_cache.get(cache_key)
            
            if cached_screenshot:
                screenshot = cached_screenshot
                self.stats['cache_hits'] += 1
            else:
                # 执行截图
                screenshot = self._capture_with_adaptive_retry(task.region)
                if screenshot:
                    self.image_cache.put(cache_key, screenshot)
                    self.stats['cache_misses'] += 1
            
            if screenshot:
                self.stats['screenshots_taken'] += 1
                processing_time = time.time() - start_time
                self.stats['total_processing_time'] += processing_time
                
                # 更新性能指标
                self.metrics.avg_capture_time = (
                    self.metrics.avg_capture_time * 0.9 + processing_time * 0.1
                )
                
                # 提交到相似度检测队列
                self.similarity_queue.put((screenshot, task, callback))
                
                return screenshot
            
        except Exception as e:
            print(f"❌ 截图任务失败 {task.task_id}: {e}")
            if callback:
                callback(None, task, False, str(e))
        
        return None
    
    def _capture_with_adaptive_retry(self, region: Tuple[int, int, int, int], 
                                   max_retries: int = 3) -> Optional[Image.Image]:
        """自适应重试截图"""
        for attempt in range(max_retries):
            try:
                # 根据系统负载调整截图质量
                if self.performance_config['adaptive_quality']:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    if cpu_percent > 80:
                        # 高负载时使用较低质量
                        screenshot = pyautogui.screenshot(region=region)
                        # 可以在这里添加图像压缩逻辑
                    else:
                        screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot(region=region)
                
                return screenshot
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 指数退避
                wait_time = 0.1 * (2 ** attempt)
                time.sleep(wait_time)
        
        return None
    
    def _similarity_processor(self):
        """相似度检测处理器"""
        last_screenshot = None
        
        while self.is_running:
            try:
                # 从队列获取任务
                item = self.similarity_queue.get(timeout=1.0)
                if item is None:
                    continue
                
                screenshot, task, callback = item
                start_time = time.time()
                
                # 执行相似度检测
                is_duplicate = False
                if last_screenshot:
                    is_duplicate = self._advanced_similarity_check(screenshot, last_screenshot)
                
                if is_duplicate:
                    self.stats['duplicates_detected'] += 1
                
                # 更新性能指标
                similarity_time = time.time() - start_time
                self.metrics.avg_similarity_time = (
                    self.metrics.avg_similarity_time * 0.9 + similarity_time * 0.1
                )
                
                # 提交到保存队列
                if not is_duplicate:
                    self.save_queue.put((screenshot, task, callback))
                    last_screenshot = screenshot
                elif callback:
                    callback(screenshot, task, False, "重复内容")
                
            except Empty:
                continue
            except Exception as e:
                print(f"⚠️ 相似度检测错误: {e}")
    
    def _advanced_similarity_check(self, img1: Image.Image, img2: Image.Image) -> bool:
        """高级相似度检测"""
        try:
            # 多级检测策略
            
            # 1. 快速哈希检测
            hash1 = self._get_fast_hash(img1)
            hash2 = self._get_fast_hash(img2)
            
            if hash1 == hash2:
                return True
            
            # 2. 感知哈希检测
            if self.performance_config['use_advanced_similarity']:
                phash1 = self._get_perceptual_hash(img1)
                phash2 = self._get_perceptual_hash(img2)
                
                # 计算汉明距离
                hamming_distance = bin(phash1 ^ phash2).count('1')
                if hamming_distance < 5:  # 阈值可调
                    return True
            
            # 3. 结构相似性检测（SSIM）
            if self.performance_config['use_advanced_similarity']:
                ssim_score = self._calculate_ssim(img1, img2)
                return ssim_score > self.performance_config['similarity_threshold']
            else:
                # 简化的相似度检测
                return self._fast_similarity_check(img1, img2)
            
        except Exception as e:
            print(f"⚠️ 高级相似度检测错误: {e}")
            return False
    
    def _get_fast_hash(self, image: Image.Image) -> str:
        """获取快速哈希"""
        # 缩小图像并转为灰度
        small_img = image.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        pixels = list(small_img.getdata())
        
        # 计算平均值
        avg = sum(pixels) / len(pixels)
        
        # 生成哈希
        hash_bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
        return hash_bits
    
    def _get_perceptual_hash(self, image: Image.Image) -> int:
        """获取感知哈希"""
        # 缩放到32x32并转为灰度
        img = image.resize((32, 32), Image.Resampling.LANCZOS).convert('L')
        pixels = np.array(img)
        
        # 计算DCT
        dct = cv2.dct(np.float32(pixels))
        
        # 取左上角8x8区域
        dct_low = dct[:8, :8]
        
        # 计算中位数
        median = np.median(dct_low)
        
        # 生成哈希
        hash_value = 0
        for i in range(8):
            for j in range(8):
                if dct_low[i, j] > median:
                    hash_value |= (1 << (i * 8 + j))
        
        return hash_value
    
    def _calculate_ssim(self, img1: Image.Image, img2: Image.Image) -> float:
        """计算结构相似性指数"""
        try:
            # 转换为灰度numpy数组
            arr1 = np.array(img1.convert('L').resize((64, 64)))
            arr2 = np.array(img2.convert('L').resize((64, 64)))
            
            # 计算均值
            mu1 = np.mean(arr1)
            mu2 = np.mean(arr2)
            
            # 计算方差和协方差
            var1 = np.var(arr1)
            var2 = np.var(arr2)
            cov = np.mean((arr1 - mu1) * (arr2 - mu2))
            
            # SSIM公式
            c1 = 0.01 ** 2
            c2 = 0.03 ** 2
            
            ssim = ((2 * mu1 * mu2 + c1) * (2 * cov + c2)) / \
                   ((mu1**2 + mu2**2 + c1) * (var1 + var2 + c2))
            
            return ssim
            
        except Exception:
            return 0.0
    
    def _fast_similarity_check(self, img1: Image.Image, img2: Image.Image) -> bool:
        """快速相似度检测（简化版）"""
        try:
            # 缩小图像进行快速比较
            size = (32, 32)
            small1 = img1.resize(size, Image.Resampling.LANCZOS).convert('L')
            small2 = img2.resize(size, Image.Resampling.LANCZOS).convert('L')
            
            # 转换为numpy数组
            arr1 = np.array(small1)
            arr2 = np.array(small2)
            
            # 计算均方误差
            mse = np.mean((arr1 - arr2) ** 2)
            
            # 相似度阈值
            threshold = 50  # 可调整
            return mse < threshold
            
        except Exception:
            return False
    
    def _batch_save_processor(self):
        """批量保存处理器"""
        save_batch = []
        last_save_time = time.time()
        batch_timeout = 2.0  # 2秒超时
        
        while self.is_running:
            try:
                # 尝试获取保存任务
                try:
                    item = self.save_queue.get(timeout=0.5)
                    if item:
                        save_batch.append(item)
                except Empty:
                    pass
                
                # 检查是否需要执行批量保存
                current_time = time.time()
                should_save = (
                    len(save_batch) >= self.performance_config['batch_save_size'] or
                    (save_batch and current_time - last_save_time > batch_timeout)
                )
                
                if should_save and save_batch:
                    self._execute_batch_save(save_batch)
                    save_batch.clear()
                    last_save_time = current_time
                
            except Exception as e:
                print(f"⚠️ 批量保存处理错误: {e}")
    
    def _execute_batch_save(self, batch: List):
        """执行批量保存"""
        start_time = time.time()
        
        # 并行保存
        futures = []
        for screenshot, task, callback in batch:
            future = self.save_executor.submit(self._save_single, screenshot, task, callback)
            futures.append(future)
        
        # 等待所有保存完成
        for future in as_completed(futures, timeout=10):
            try:
                future.result()
            except Exception as e:
                print(f"❌ 单个保存任务失败: {e}")
        
        # 更新性能指标
        save_time = time.time() - start_time
        self.metrics.avg_save_time = (
            self.metrics.avg_save_time * 0.9 + save_time * 0.1
        )
    
    def _save_single(self, screenshot: Image.Image, task: ScreenshotTask, 
                    callback: Optional[Callable] = None):
        """保存单个截图"""
        try:
            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(task.timestamp))
            filename = f"screenshot_{timestamp}_{task.task_id:04d}.png"
            
            # 使用配置的保存路径
            filepath = os.path.join(self.save_directory, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存截图
            save_kwargs = {
                'optimize': True,
                'compress_level': self.performance_config['compression_level']
            }
            screenshot.save(filepath, 'PNG', **save_kwargs)
            
            if callback:
                callback(screenshot, task, True, filepath)
                
        except Exception as e:
            print(f"❌ 保存截图失败: {e}")
            if callback:
                callback(screenshot, task, False, str(e))
    
    def _performance_monitor(self):
        """性能监控器"""
        while self.is_running:
            try:
                # 更新内存使用情况
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024**2)
                self.metrics.memory_usage_mb = memory_mb
                
                # 检查内存限制
                if memory_mb > self.performance_config['memory_limit_mb']:
                    print(f"⚠️ 内存使用超限: {memory_mb:.1f}MB")
                    self._cleanup_memory()
                
                # 更新缓存命中率
                self.metrics.cache_hit_rate = self.image_cache.get_hit_rate()
                
                # 计算吞吐量
                if self.stats['total_processing_time'] > 0:
                    self.metrics.throughput_fps = (
                        self.stats['screenshots_taken'] / self.stats['total_processing_time']
                    )
                
                time.sleep(5)  # 每5秒监控一次
                
            except Exception as e:
                print(f"⚠️ 性能监控错误: {e}")
    
    def _cleanup_memory(self):
        """清理内存"""
        # 清理缓存
        self.image_cache.clear()
        self.hash_cache.clear()
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        print("🧹 内存清理完成")
    
    def get_adaptive_wait_time(self, scroll_mode: str) -> float:
        """获取自适应等待时间"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return self.wait_manager.calculate_wait_time(scroll_mode, cpu_percent)
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        return self.metrics
    
    def get_detailed_stats(self) -> dict:
        """获取详细统计信息"""
        stats = self.stats.copy()
        stats.update({
            'cache_hit_rate': self.metrics.cache_hit_rate,
            'avg_capture_time': self.metrics.avg_capture_time,
            'avg_similarity_time': self.metrics.avg_similarity_time,
            'avg_save_time': self.metrics.avg_save_time,
            'memory_usage_mb': self.metrics.memory_usage_mb,
            'throughput_fps': self.metrics.throughput_fps,
            'queue_sizes': {
                'capture': self.capture_queue.qsize(),
                'similarity': self.similarity_queue.qsize(),
                'save': self.save_queue.qsize()
            }
        })
        return stats
    
    def cleanup(self):
        """清理资源"""
        print("🧹 开始清理高级截图管理器...")
        
        self.is_running = False
        
        # 关闭线程池
        self.capture_executor.shutdown(wait=True, timeout=5)
        self.similarity_executor.shutdown(wait=True, timeout=5)
        self.save_executor.shutdown(wait=True, timeout=5)
        
        # 清理缓存
        self.image_cache.clear()
        self.hash_cache.clear()
        
        print("✅ 高级截图管理器清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()


# 使用示例
if __name__ == "__main__":
    import cv2  # 确保导入cv2
    
    # 创建高级截图管理器
    manager = AdvancedScreenshotManager()
    
    try:
        # 测试异步截图
        region = (100, 100, 800, 600)
        
        def screenshot_callback(screenshot, task, success, result):
            if success:
                print(f"✅ 截图任务 {task.task_id} 完成: {result}")
            else:
                print(f"❌ 截图任务 {task.task_id} 失败: {result}")
        
        # 提交多个截图任务
        for i in range(5):
            task_id = manager.capture_screenshot_async(region, screenshot_callback)
            print(f"📸 提交截图任务 {task_id}")
            time.sleep(0.5)
        
        # 等待处理完成
        time.sleep(5)
        
        # 显示性能统计
        metrics = manager.get_performance_metrics()
        stats = manager.get_detailed_stats()
        
        print(f"\n📊 性能指标:")
        print(f"   平均截图时间: {metrics.avg_capture_time:.3f}s")
        print(f"   平均相似度检测时间: {metrics.avg_similarity_time:.3f}s")
        print(f"   平均保存时间: {metrics.avg_save_time:.3f}s")
        print(f"   内存使用: {metrics.memory_usage_mb:.1f}MB")
        print(f"   缓存命中率: {metrics.cache_hit_rate:.2%}")
        print(f"   吞吐量: {metrics.throughput_fps:.1f} FPS")
        
        print(f"\n📈 详细统计:")
        for key, value in stats.items():
            if key != 'queue_sizes':
                print(f"   {key}: {value}")
        
    finally:
        manager.cleanup()