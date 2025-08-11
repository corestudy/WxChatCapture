#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能滚动截图工具 - 测试包

这个包包含了项目的所有测试模块。

测试模块说明:
- test_performance: 性能测试
- test_ui: 用户界面测试

使用方法:
    python -m pytest tests/
    或
    python tests/test_performance.py
"""

__version__ = "3.0.6"

# 测试配置
import sys
import os

# 添加源代码路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 测试工具函数
def setup_test_environment():
    """设置测试环境"""
    # 确保测试目录存在
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir)
    
    return test_data_dir

def cleanup_test_environment():
    """清理测试环境"""
    import shutil
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

# 导出测试工具
__all__ = [
    'setup_test_environment',
    'cleanup_test_environment'
]