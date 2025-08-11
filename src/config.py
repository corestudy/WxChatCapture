#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能滚动截图工具 v3.0 - 配置管理模块

管理应用程序的配置参数和设置。

作者: 智能截图工具开发团队
版本: 3.0.1
许可: MIT 许可证
"""

# 标准库导入
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

# 项目配置
__version__ = "3.0.6"
__author__ = "智能截图工具开发团队"


@dataclass
class AppConfig:
    """应用程序配置类"""
    
    # 应用信息
    app_name: str = "智能滚动截图工具"
    app_version: str = "3.0.6"
    
    # 窗口设置
    window_width: int = 520
    window_height: int = 850
    window_resizable: bool = True
    window_min_width: int = 480
    window_min_height: int = 700
    
    # 截图设置
    default_interval: float = 0.3
    min_interval: float = 0.1
    max_interval: float = 5.0
    auto_detect_similarity: bool = True
    similarity_threshold: float = 0.001
    
    # 滚动设置
    default_scroll_mode: str = "mouse"  # "mouse" 或 "page"
    default_scroll_direction: str = "down"  # "down" 或 "up"
    page_scroll_wait: float = 0.5
    mouse_scroll_wait: float = 0.3
    
    # 文件设置
    default_save_dir: str = "微信聊天记录"
    image_format: str = "png"
    image_quality: int = 95
    filename_pattern: str = "screenshot_{timestamp}_{count:04d}.{ext}"
    
    # 性能设置
    max_consecutive_errors: int = 3
    ui_update_interval: int = 100  # 毫秒
    memory_cleanup_interval: int = 10  # 每N张截图清理一次内存
    
    # 界面设置
    theme: str = "light"  # "light" 或 "dark"
    language: str = "zh_CN"  # "zh_CN" 或 "en_US"
    show_tooltips: bool = True
    
    # 日志设置
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    log_to_file: bool = True
    max_log_files: int = 10
    
    # 证据记录设置
    enable_evidence_recording: bool = False
    evidence_case_id: str = ""
    evidence_operator: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置对象"""
        # 过滤掉不存在的字段
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config = AppConfig()
        self.load()
    
    def load(self) -> None:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = AppConfig.from_dict(data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
                self.config = AppConfig()
        else:
            # 首次运行，创建默认配置文件
            self.save()
    
    def save(self) -> None:
        """保存配置文件"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
        except (OSError, PermissionError) as e:
            print(f"配置文件保存失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save()
        else:
            raise ValueError(f"未知的配置键: {key}")
    
    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = AppConfig()
        self.save()
    
    def update(self, **kwargs) -> None:
        """
        批量更新配置
        
        Args:
            **kwargs: 配置键值对
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"警告: 忽略未知的配置键 '{key}'")
        self.save()


# 全局配置管理器实例
config_manager = ConfigManager()

# 便捷访问函数
def get_config() -> AppConfig:
    """获取当前配置"""
    return config_manager.config

def get_setting(key: str, default: Any = None) -> Any:
    """获取配置项"""
    return config_manager.get(key, default)

def set_setting(key: str, value: Any) -> None:
    """设置配置项"""
    config_manager.set(key, value)

def save_config() -> None:
    """保存配置"""
    config_manager.save()

# 导出的公共API
__all__ = [
    'AppConfig',
    'ConfigManager',
    'config_manager',
    'get_config',
    'get_setting',
    'set_setting',
    'save_config'
]