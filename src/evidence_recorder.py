"""
证据记录模块 - 为智能滚动截图工具提供证据链记录和屏幕录制功能
"""

import hashlib
import json
import platform
import getpass
import time
import threading
import cv2
import numpy as np
import pyautogui
from datetime import datetime
from pathlib import Path
import psutil
import os

class EvidenceRecorder:
    """证据记录器 - 核心功能"""
    
    def __init__(self, case_id=None):
        self.case_id = case_id or self.generate_case_id()
        self.evidence_chain = []
        self.system_info = self.collect_system_info()
        
    def generate_case_id(self):
        """生成案件ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"WECHAT_CASE_{timestamp}"
    
    def collect_system_info(self):
        """收集系统信息"""
        try:
            return {
                'os_name': platform.system(),
                'os_version': platform.version(),
                'hostname': platform.node(),
                'operator': getpass.getuser(),
                'screen_resolution': list(pyautogui.size()),
                'timezone': time.tzname[0] if time.tzname[0] else 'UTC',
                'python_version': platform.python_version(),
                'capture_tool': 'WeChat Evidence Tool v3.1'
            }
        except Exception as e:
            return {'error': f'Failed to collect system info: {e}'}
    
    def record_evidence(self, screenshot, region, context=None):
        """记录证据"""
        timestamp = datetime.now()
        
        # 计算图像哈希
        image_hash = self.calculate_image_hash(screenshot)
        
        # 创建证据记录
        evidence = {
            'evidence_id': f"EVD_{len(self.evidence_chain) + 1:06d}",
            'case_id': self.case_id,
            'timestamp': timestamp.isoformat(),
            'unix_timestamp': timestamp.timestamp(),
            'image_hash_sha256': image_hash,
            'image_size': {'width': screenshot.width, 'height': screenshot.height},
            'capture_region': {
                'x': region[0], 'y': region[1], 
                'width': region[2], 'height': region[3]
            } if region else None,
            'context': context or {},
            'file_info': None  # 稍后填充
        }
        
        self.evidence_chain.append(evidence)
        return evidence
    
    def calculate_image_hash(self, image):
        """计算图像哈希"""
        image_bytes = image.tobytes()
        return hashlib.sha256(image_bytes).hexdigest()
    
    def update_file_info(self, evidence_id, file_path):
        """更新文件信息"""
        for evidence in self.evidence_chain:
            if evidence['evidence_id'] == evidence_id:
                evidence['file_info'] = {
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size if file_path.exists() else 0,
                    'file_hash': self.calculate_file_hash(file_path)
                }
                break
    
    def calculate_file_hash(self, file_path):
        """计算文件哈希"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None
    
    def export_evidence_chain(self, output_path):
        """导出证据链"""
        evidence_package = {
            'case_info': {
                'case_id': self.case_id,
                'created_at': datetime.now().isoformat(),
                'total_evidence': len(self.evidence_chain)
            },
            'system_info': self.system_info,
            'evidence_chain': self.evidence_chain,
            'integrity': {
                'chain_hash': self.calculate_chain_hash(),
                'generated_at': datetime.now().isoformat()
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(evidence_package, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def calculate_chain_hash(self):
        """计算证据链哈希"""
        chain_data = json.dumps(self.evidence_chain, sort_keys=True)
        return hashlib.sha256(chain_data.encode()).hexdigest()

class ScreenRecorder:
    """屏幕录制器 - 核心功能"""
    
    def __init__(self, output_dir="recordings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.recording = False
        self.video_writer = None
        self.record_thread = None
        self.fps = 10
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        self.current_file = None
        self.start_time = None
    
    def start_recording(self, region=None):
        """开始录制"""
        if self.recording:
            return False
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wechat_evidence_{timestamp}.mp4"
        self.current_file = self.output_dir / filename
        
        # 确定录制区域
        if region is None:
            screen_size = pyautogui.size()
            self.record_region = (0, 0, screen_size.width, screen_size.height)
        else:
            self.record_region = region
        
        # 初始化录制
        frame_size = (self.record_region[2], self.record_region[3])
        self.video_writer = cv2.VideoWriter(
            str(self.current_file), self.codec, self.fps, frame_size
        )
        
        if not self.video_writer.isOpened():
            return False
        
        # 开始录制
        self.recording = True
        self.start_time = datetime.now()
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        
        return True
    
    def stop_recording(self):
        """停止录制"""
        if not self.recording:
            return None
        
        self.recording = False
        
        # 等待线程结束
        if self.record_thread:
            self.record_thread.join(timeout=3)
        
        # 释放资源
        if self.video_writer:
            self.video_writer.release()
        
        # 返回录制信息
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            'file_path': str(self.current_file),
            'duration': duration,
            'file_size': self.current_file.stat().st_size if self.current_file.exists() else 0,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'region': self.record_region
        }
    
    def _record_loop(self):
        """录制循环"""
        frame_interval = 1.0 / self.fps
        
        while self.recording:
            try:
                start = time.time()
                
                # 截取屏幕
                screenshot = pyautogui.screenshot(region=self.record_region)
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # 写入视频
                if self.video_writer:
                    self.video_writer.write(frame)
                
                # 控制帧率
                elapsed = time.time() - start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"录制错误: {e}")
                break
    
    def is_recording(self):
        """检查录制状态"""
        return self.recording
    
    def get_status(self):
        """获取录制状态"""
        if self.recording and self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            return {
                'status': 'recording',
                'duration': duration,
                'file_path': str(self.current_file)
            }
        return {'status': 'stopped', 'duration': 0, 'file_path': None}

class EnhancedSaver:
    """增强截图保存器"""
    
    def __init__(self, evidence_recorder, output_dir="evidence_screenshots"):
        self.evidence_recorder = evidence_recorder
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_evidence_screenshot(self, screenshot, region, context=None):
        """保存证据截图"""
        # 记录证据
        evidence = self.evidence_recorder.record_evidence(screenshot, region, context)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = f"{evidence['evidence_id']}_{timestamp}.png"
        file_path = self.output_dir / filename
        
        try:
            # 保存截图
            screenshot.save(file_path, "PNG")
            
            # 更新文件信息
            self.evidence_recorder.update_file_info(evidence['evidence_id'], file_path)
            
            # 保存元数据
            metadata_path = file_path.with_suffix('.json')
            self._save_metadata(evidence, metadata_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'evidence_id': evidence['evidence_id']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save_metadata(self, evidence, metadata_path):
        """保存元数据"""
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(evidence, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存元数据失败: {e}")