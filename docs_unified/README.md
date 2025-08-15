# 📚 文档中心（统一版） v3.0.6

> 本页为“单页总览 + 细分章节”的统一文档，覆盖快速开始、安装配置、功能使用、故障排除、开发指南、API 参考、技术实现、项目架构与合规指南等内容。原来散布在 docs_unified/ 的多个章节文档均已合并于此，原文件暂时保留以方便溯源与对比，后续参考请以本页为准。

- 适用版本：v3.0.6
- 支持系统：Windows 10/11
- Python 版本：3.7+

---

## 目录
- [📚 文档中心（统一版） v3.0.6](#-文档中心统一版-v306)
  - [目录](#目录)
  - [快速开始](#快速开始)
  - [安装与配置](#安装与配置)
  - [功能使用](#功能使用)
  - [故障排除](#故障排除)
  - [开发环境与流程](#开发环境与流程)
  - [API 参考](#api-参考)
  - [技术实现概览](#技术实现概览)
  - [项目架构](#项目架构)
  - [法律合规指南](#法律合规指南)
  - [文档维护规范](#文档维护规范)
  - [贡献指南](#贡献指南)
  - [项目文件结构](#项目文件结构)
  - [接口兼容说明](#接口兼容说明)
  - [附：常见命令速查](#附常见命令速查)

---

## 快速开始

1) 安装依赖

```bash
pip install -r requirements.txt
```

2) 启动程序

```bash
# 方式一：直接运行
python src/main.py

# 方式二：控制台脚本（安装后）
smart-screenshot
```

3) 基本操作
- 选择区域 → 拖拽需要截图的区域
- 选择滚动模式（鼠标滚轮 或 Page 键）与方向
- 点击“开始截图”；可选勾选“纯滚动模式（不截图）”
- 录屏：在“屏幕录制”卡片设置 FPS（10–30），选择“选定区域/全屏”，开始/停止

4) 输出位置
- 截图保存在设置的“保存目录”（默认项目根目录中的“微信聊天记录”）
- 录制视频保存在 保存目录/录制视频/

---

## 安装与配置

- 支持：Windows 10/11，Python 3.7+
- 依赖：Pillow>=9.0.0、PyAutoGUI>=0.9.54、numpy>=1.21.0、pywinauto、keyboard、opencv-python、psutil（合规模块可选安装 cryptography）

常用命令：
```bash
# 安装核心依赖
pip install -r requirements.txt

# 开发依赖（建议，含格式化/静态检查等）
pip install -e ".[dev]"

# Windows 启动器（统一菜单）
scripts\run.bat
```

配置文件（自动生成）：`config.json`，通过 GUI 或 `src/config.py` 的 `ConfigManager` 读写。

---

## 功能使用

- 滚动截图：
  - 模式：Page 键 / 鼠标滚轮
  - 重复检测：开启“智能检测重复内容自动停止”，避免重复页
  - 保存命名：`screenshot_{timestamp}_{count:04d}.png`
- 区域录屏：
  - 选择：选定区域 / 全屏
  - FPS：10–30，编码：mp4v → mp4
  - 输出：保存目录/录制视频/
- 微信优化：可配合 `src/wechat_detector.py` 自动定位最佳聊天区（message_list）

---

## 故障排除

- 环境/依赖：运行 `python tools/check_imports.py`
- 启动失败：运行 `python tools/debug_run.py` 查看详细日志
- Tkinter 缺失：使用带 Tcl/Tk 的官方 Python 发行版；或重装/修复 Python
- 权限问题（keyboard/pywinauto）：以管理员权限运行或降低系统防护策略
- 无头/远程环境：GUI 程序需桌面环境，CI/服务器场景请勿运行

---

## 开发环境与流程

- 代码风格：Black + isort + Flake8 + Mypy
- 预提交钩子：`pre-commit install`
- 常用 Make 目标：
```bash
make install        # 安装依赖
make install-dev    # 安装开发依赖+pre-commit
make lint           # flake8/mypy/bandit
make format         # black/isort
make build          # 构建分发
```

---

## API 参考

- 核心类：
  - `ScrollScreenshotApp`（GUI 主应用）
  - `ScrollController`（滚动控制）
  - `EvidenceRecorder` / `ScreenRecorder`（证据链与录屏）
  - `ConfigManager`（配置管理）
  - `WeChatDetector`（微信窗口检测/区域推断）
- 兼容性接口：
  - `select_region()` ⇆ `start_region_selection()`
  - `region` 属性返回 `(x, y, width, height)`

---

## 技术实现概览

- 截图/录屏：PyAutoGUI + OpenCV
- 相似度检测：采样差异/直方图/哈希/SSIM（在优化/高级管理器中）
- 异步流水线：线程池 + 队列 + 批量保存（优化/高级管理器）
- 性能与稳定性：自适应等待、缓冲与跳帧、内存清理、错误重试

---

## 项目架构

- src/ 主干：GUI、工具、配置、合规、微信检测
- tools/：依赖检查、调试运行、快速启动、可视化测试
- scripts/：Windows 启动器 run.bat
- docs_unified/：统一文档（本页）

---

## 法律合规指南

- 目标：保证电子证据的真实性、完整性、合法性、关联性、可追溯性
- 机制：SHA256 哈希、证据链记录（时间戳/操作者/系统信息）、数字签名（可选 cryptography）
- 标准：GB/T 29360-2012、ISO/IEC 27037:2012

---

## 文档维护规范

- 统一“单文档”原则：以本页为准，其他文档作为补充或历史材料
- 版本标注：统一 v3.0.6
- 更新流程：功能变更 → 同步本页对应章节 → CHANGELOG 标注

---

## 贡献指南

- 流程：Fork → 分支 → 开发/测试 → 提交 PR
- 规范：提交信息（feat/fix/docs/...），PEP8/Black，必要文档与测试
- 优先方向：Bug 修复、性能优化、文档完善、测试覆盖

---

## 项目文件结构

见根 README 与本页“项目架构”章节；详细文件映射与整理报告见：
- CODE_ORGANIZATION_REPORT.md（代码整理报告）
- FINAL_FILE_ORGANIZATION_REPORT.md（最终文件整理报告）

---

## 接口兼容说明

- ScrollScreenshotApp 已提供向后兼容接口：
  - `select_region()` 作为 `start_region_selection()` 的别名
  - `region` 属性返回当前选区四元组
- 工具脚本已兼容两套命名（debug_run/simple_test）

---

## 附：常见命令速查

```bash
# 依赖检查 / 调试运行 / 快速启动 / 可视化测试
python tools/check_imports.py
python tools/debug_run.py
python tools/quick_start.py
python tools/simple_test.py

# 主程序
python src/main.py
smart-screenshot

# Windows 启动器
scripts\run.bat
```

---

文档维护：活跃维护中（最后更新：2024-12-19）。如有问题，请在 [GitHub Issues](https://github.com/smartscreenshot/smart-screenshot-tool/issues) 提交系统版本、Python 版本与复现步骤。
