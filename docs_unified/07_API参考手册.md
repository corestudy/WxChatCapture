# 📖 API参考手册 v3.0.6

## 🎯 概述

本文档提供智能滚动截图工具的完整API参考，包括所有主要类、方法和接口的详细说明。无论您是要集成工具到自己的项目中，还是要扩展工具的功能，本文档都将为您提供必要的技术参考。

### 📚 API特色
- **完整覆盖**: 涵盖所有公开的类和方法
- **详细说明**: 每个API都有详细的参数和返回值说明
- **实用示例**: 提供丰富的代码示例和使用场景
- **版本兼容**: 明确标注API的版本兼容性

## 🔧 核心类

### ScrollScreenshotApp

主应用类，提供完整的GUI界面和截图功能。

#### 初始化
```python
from src.main import ScrollScreenshotApp
import tkinter as tk

# 基本初始化
root = tk.Tk()
app = ScrollScreenshotApp(root)

# 高级初始化（带配置）
from src.config import AppConfig
config = AppConfig()
config.ui["theme"] = "modern"
config.screenshot["quality"] = 95
app = ScrollScreenshotApp(root, config=config)
```

#### 类属性
- `root`: Tkinter主窗口
- `is_capturing`: 截图状态标志
- `scroll_controller`: 滚动控制器实例
- `region`: 当前选择的截图区域
- `save_path`: 截图保存路径
- `screenshot_count`: 已截图数量

#### 主要方法

##### select_region()
选择截图区域
```python
def select_region(self):
    """
    启动区域选择功能
    
    Returns:
        tuple: 选择的区域坐标 (x, y, width, height)
    """
```

##### start_capture()
开始截图
```python
def start_capture(self):
    """
    开始自动滚动截图
    
    Returns:
        bool: 启动是否成功
    """
```

##### stop_capture()
停止截图
```python
def stop_capture(self):
    """
    停止当前截图任务
    """
```

##### capture_screenshot()
单次截图
```python
def capture_screenshot(self, region=None):
    """
    捕获单张截图
    
    Args:
        region (tuple, optional): 截图区域，默认使用当前选择区域
    
    Returns:
        PIL.Image: 截图图像对象
    """
```

### ScrollController

智能滚动控制器，支持多种滚动模式。

#### 初始化
```python
from src.main import ScrollController

controller = ScrollController()
```

#### 主要方法

##### dynamic_scroll()
执行智能滚动
```python
def dynamic_scroll(self, direction="down", mode="mouse", region=None, app_instance=None):
    """
    执行智能滚动操作
    
    Args:
        direction (str): 滚动方向 ("down", "up")
        mode (str): 滚动模式 ("mouse", "page")
        region (tuple): 滚动区域坐标
        app_instance: 应用实例引用
    
    Returns:
        bool: 滚动是否成功
    """
```

##### stop()
停止滚动
```python
def stop(self):
    """
    停止滚动操作
    """
```

### EvidenceRecorder

证据记录器，提供法律取证功能。

#### 初始化
```python
from src.evidence_recorder import EvidenceRecorder

recorder = EvidenceRecorder(case_id="CASE001")
```

#### 主要方法

##### start_recording()
开始证据记录
```python
def start_recording(self, evidence_type="screenshot"):
    """
    开始证据记录
    
    Args:
        evidence_type (str): 证据类型 ("screenshot", "video", "document")
    
    Returns:
        str: 记录会话ID
    """
```

##### add_evidence()
添加证据
```python
def add_evidence(self, file_path, metadata=None):
    """
    添加证据文件
    
    Args:
        file_path (str): 证据文件路径
        metadata (dict): 证据元数据
    
    Returns:
        dict: 证据记录信息
    """
```

##### generate_report()
生成证据报告
```python
def generate_report(self, output_path):
    """
    生成证据链报告
    
    Args:
        output_path (str): 报告输出路径
    
    Returns:
        str: 生成的报告文件路径
    """
```

## 🎨 UI组件API

### 区域选择器

#### RegionSelector
```python
class RegionSelector:
    def __init__(self, parent):
        """
        初始化区域选择器
        
        Args:
            parent: 父窗口对象
        """
    
    def select_region(self):
        """
        启动区域选择
        
        Returns:
            tuple: (x, y, width, height)
        """
    
    def get_region(self):
        """
        获取当前选择的区域
        
        Returns:
            tuple: 区域坐标
        """
```

### 状态显示器

#### StatusDisplay
```python
class StatusDisplay:
    def update_status(self, status, details=None):
        """
        更新状态显示
        
        Args:
            status (str): 状态文本
            details (dict): 详细信息
        """
    
    def show_progress(self, current, total):
        """
        显示进度
        
        Args:
            current (int): 当前进度
            total (int): 总数
        """
```

## 🔧 配置API

### AppConfig

应用配置管理器

#### 配置结构
```python
config = {
    "ui": {
        "theme": "modern",
        "window_size": (800, 600),
        "font_size": 12
    },
    "screenshot": {
        "quality": 95,
        "format": "PNG",
        "auto_save": True
    },
    "scroll": {
        "mode": "mouse",
        "interval": 0.3,
        "similarity_threshold": 0.95
    },
    "evidence": {
        "enable_recording": True,
        "hash_algorithm": "SHA256",
        "encryption": False
    }
}
```

#### 配置方法
```python
from src.config import AppConfig

# 加载配置
config = AppConfig()
config.load_from_file("config.json")

# 获取配置值
theme = config.get("ui.theme", "default")
quality = config.get("screenshot.quality", 90)

# 设置配置值
config.set("ui.theme", "dark")
config.set("screenshot.quality", 100)

# 保存配置
config.save_to_file("config.json")
```

## 🎥 录屏API

### ScreenRecorder

屏幕录制器

#### 初始化
```python
from src.evidence_recorder import ScreenRecorder

recorder = ScreenRecorder(
    region=(0, 0, 1920, 1080),
    fps=10,
    output_path="recording.mp4"
)
```

#### 主要方法

##### start_recording()
开始录制
```python
def start_recording(self):
    """
    开始屏幕录制
    
    Returns:
        bool: 启动是否成功
    """
```

##### stop_recording()
停止录制
```python
def stop_recording(self):
    """
    停止录制并保存文件
    
    Returns:
        str: 录制文件路径
    """
```

##### get_recording_info()
获取录制信息
```python
def get_recording_info(self):
    """
    获取当前录制信息
    
    Returns:
        dict: 录制状态和统计信息
    """
```

## 🛠️ 工具函数API

### 图像处理

#### image_similarity()
计算图像相似度
```python
from src.utils import image_similarity

similarity = image_similarity(image1, image2, method="ssim")
```

#### optimize_image()
优化图像
```python
from src.utils import optimize_image

optimized = optimize_image(image, quality=95, format="PNG")
```

### 文件操作

#### generate_filename()
生成文件名
```python
from src.utils import generate_filename

filename = generate_filename(
    prefix="screenshot",
    timestamp=True,
    extension="png"
)
```

#### ensure_directory()
确保目录存在
```python
from src.utils import ensure_directory

ensure_directory("/path/to/screenshots")
```

## 🔒 安全API

### 哈希计算

#### calculate_hash()
计算文件哈希
```python
from src.utils import calculate_hash

hash_value = calculate_hash("/path/to/file", algorithm="SHA256")
```

### 加密功能

#### encrypt_file()
加密文件
```python
from src.utils import encrypt_file

encrypted_path = encrypt_file(
    file_path="/path/to/file",
    password="secure_password",
    algorithm="AES-256"
)
```

## 📊 事件系统

### 事件类型

#### 截图事件
- `screenshot_started`: 截图开始
- `screenshot_completed`: 截图完成
- `screenshot_failed`: 截图失败

#### 滚动事件
- `scroll_started`: 滚动开始
- `scroll_completed`: 滚动完成
- `scroll_failed`: 滚动失败

#### 录制事件
- `recording_started`: 录制开始
- `recording_stopped`: 录制停止
- `recording_error`: 录制错误

### 事件监听

#### 注册事件监听器
```python
from src.main import ScrollScreenshotApp

app = ScrollScreenshotApp(root)

def on_screenshot_completed(event_data):
    print(f"截图完成: {event_data['filename']}")

app.register_event_listener("screenshot_completed", on_screenshot_completed)
```

## 🧪 测试API

### 测试工具

#### MockScreenshot
模拟截图功能
```python
from tests.mocks import MockScreenshot

mock = MockScreenshot()
mock.set_region((100, 100, 500, 400))
image = mock.capture()
```

#### TestHelper
测试辅助工具
```python
from tests.helpers import TestHelper

helper = TestHelper()
helper.setup_test_environment()
helper.create_test_images()
helper.cleanup_test_files()
```

## 📋 错误处理

### 异常类型

#### ScreenshotError
截图相关错误
```python
class ScreenshotError(Exception):
    """截图操作失败"""
    pass
```

#### RegionError
区域选择错误
```python
class RegionError(Exception):
    """区域选择无效"""
    pass
```

#### RecordingError
录制相关错误
```python
class RecordingError(Exception):
    """录制操作失败"""
    pass
```

### 错误处理示例
```python
try:
    app.start_capture()
except ScreenshotError as e:
    print(f"截图失败: {e}")
except RegionError as e:
    print(f"区域选择错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 📚 使用示例

### 基本截图流程
```python
import tkinter as tk
from src.main import ScrollScreenshotApp

# 创建应用
root = tk.Tk()
app = ScrollScreenshotApp(root)

# 选择区域
region = app.select_region()
print(f"选择的区域: {region}")

# 开始截图
app.start_capture()

# 运行GUI
root.mainloop()
```

### 证据记录流程
```python
from src.evidence_recorder import EvidenceRecorder

# 创建证据记录器
recorder = EvidenceRecorder(case_id="CASE001")

# 开始记录
session_id = recorder.start_recording("screenshot")

# 添加证据
evidence_info = recorder.add_evidence(
    file_path="screenshot_001.png",
    metadata={
        "timestamp": "2024-12-19 10:30:00",
        "operator": "张三",
        "description": "微信聊天记录第1页"
    }
)

# 生成报告
report_path = recorder.generate_report("evidence_report.pdf")
```

### 自定义配置
```python
from src.config import AppConfig
from src.main import ScrollScreenshotApp

# 创建自定义配置
config = AppConfig()
config.set("screenshot.quality", 100)
config.set("scroll.interval", 0.2)
config.set("ui.theme", "dark")

# 使用配置创建应用
root = tk.Tk()
app = ScrollScreenshotApp(root, config=config)
```

---

**API版本**: v3.0.6  
**兼容性**: Python 3.7+  
**维护状态**: 活跃维护

> 📖 **说明**: 本API文档提供了完整的接口说明和使用示例，帮助开发者快速集成和扩展功能。