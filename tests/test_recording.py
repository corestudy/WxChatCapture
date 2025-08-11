#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录屏功能测试脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    import cv2
    print("✅ OpenCV 导入成功")
    print(f"OpenCV 版本: {cv2.__version__}")
except ImportError as e:
    print("❌ OpenCV 导入失败:", e)
    print("请安装 OpenCV: pip install opencv-python")
    sys.exit(1)

try:
    from datetime import datetime
    from pathlib import Path
    print("✅ 其他依赖导入成功")
except ImportError as e:
    print("❌ 依赖导入失败:", e)
    sys.exit(1)

def test_video_writer():
    """测试视频写入器"""
    try:
        # 测试参数
        filename = "test_video.mp4"
        fps = 10
        frame_size = (800, 600)
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        # 创建视频写入器
        writer = cv2.VideoWriter(filename, codec, fps, frame_size)
        
        if writer.isOpened():
            print("✅ 视频写入器创建成功")
            writer.release()
            
            # 清理测试文件
            if os.path.exists(filename):
                os.remove(filename)
            return True
        else:
            print("❌ 视频写入器创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 视频写入器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎥 录屏功能依赖测试")
    print("=" * 40)
    
    # 测试视频写入器
    if test_video_writer():
        print("✅ 录屏功能依赖测试通过")
        print("\n现在可以运行主程序测试录屏功能:")
        print("python src/main.py")
    else:
        print("❌ 录屏功能依赖测试失败")
        print("请检查 OpenCV 安装")

if __name__ == "__main__":
    main()