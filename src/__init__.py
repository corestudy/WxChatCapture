#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能滚动截图工具 v3.0 - 源代码包

这个包包含了智能滚动截图工具的核心功能模块。

模块说明:
- main: 主程序和GUI界面
- evidence_recorder: 证据记录和屏幕录制功能

作者: 智能截图工具开发团队
版本: 3.0.6
许可: MIT 许可证
"""

__version__ = "3.0.8"
__author__ = "智能截图工具开发团队"
__email__ = "support@screenshot-tool.com"
__license__ = "MIT"

# 导入主要类和函数
try:
    from .main import ScrollScreenshotApp, ScrollController
    from .evidence_recorder import EvidenceRecorder, ScreenRecorder
    from .utils import Logger, PathValidator, UIHelper, PerformanceMonitor
    from .config import ConfigManager, get_config, get_setting, set_setting
except ImportError as e:
    print(f"警告: 模块导入失败 - {e}")
    # 提供基本的占位符类
    class ScrollScreenshotApp: pass
    class ScrollController: pass
    class EvidenceRecorder: pass
    class ScreenRecorder: pass

# 定义公共API
__all__ = [
    "ScrollScreenshotApp",
    "ScrollController", 
    "EvidenceRecorder",
    "ScreenRecorder",
    "Logger",
    "PathValidator",
    "UIHelper", 
    "PerformanceMonitor",
    "ConfigManager",
    "get_config",
    "get_setting",
    "set_setting",
    "__version__",
    "__author__",
]

# 版本兼容性检查
import sys
if sys.version_info < (3, 7):
    raise RuntimeError("此工具需要Python 3.7或更高版本")

# 依赖检查
def check_dependencies():
    """检查必要的依赖包是否已安装"""
    required_packages = [
        'tkinter',
        'PIL', 
        'pyautogui',
        'numpy',
        'cv2',
        'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(f"缺少必要的依赖包: {', '.join(missing_packages)}")

# 自动检查依赖
try:
    check_dependencies()
except ImportError as e:
    print(f"警告: {e}")
    print("请运行: pip install -r requirements.txt")