# 智能滚动截图工具 (Smart Screenshot Tool) v3.0.6

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![OS](https://img.shields.io/badge/os-Windows%2010%2F11-informational.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-3.0.6-blue.svg)

**智能滚动截图工具**是一款专为微信聊天记录取证、长网页、长文档截图而设计的高级工具。它集成了智能滚动、重复内容检测、区域录屏和符合法律规范的证据链记录功能。

---

## 核心功能

- **智能滚动截图**：支持鼠标滚轮和PageDown/Up按键两种滚动模式，能智能检测页面末尾并自动停止。
- **区域/全屏录屏**：可录制选定区域或整个屏幕，并保存为MP4视频文件。
- **微信窗口优化**：能够自动检测微信PC版窗口，并精准定位聊天记录区域进行截图。
- **法律合规证据链**：在截图时生成包含时间戳、操作员信息和SHA256哈希值的证据记录，确保电子证据的真实性和完整性，符合司法鉴定标准。
- **高性能处理**：采用异步处理、多线程和缓存机制，确保截图和录屏过程流畅高效。

---

## 快速开始

### 1. 安装依赖

确保你的环境为 **Windows 10/11** 和 **Python 3.7+**。

```bash
pip install -r requirements.txt
```

### 2. 启动程序

```bash
# 方式一：直接运行
python src/main.py

# 方式二：通过控制台脚本 (需要先通过 setup.py 或 pyproject.toml 安装)
smart-screenshot
```

### 3. 基本操作

1.  **选择区域**：点击 "选择区域" 按钮，然后拖拽鼠标框选你需要截图或录屏的范围。
2.  **配置参数**：
    *   **滚动截图**：选择滚动模式（鼠标或Page键）、滚动方向和每次滚动的间隔时间。
    *   **屏幕录制**：设置录制的帧率（FPS）和录制范围（选定区域或全屏）。
3.  **开始任务**：
    *   点击 "开始截图" 或 "开始录制"。
    *   点击 "停止" 按钮来结束任务。

### 4. 查看产出

-   **截图**：默认保存在项目根目录下的 `微信聊天记录` 文件夹中。
-   **录屏**：默认保存在 `[保存目录]/录制视频/` 文件夹中。
-   你可以在UI界面上修改默认的保存位置。

---

## 项目结构

```
/
├── src/                # 核心源代码
│   ├── main.py         # GUI和主应用逻辑
│   ├── wechat_detector.py # 微信窗口检测
│   ├── evidence_recorder.py # 证据记录与屏幕录制
│   ├── legal_compliance.py  # 法律合规模块
│   └── ...
├── tools/              # 辅助开发者工具 (如依赖检查、调试运行)
├── scripts/            # 自动化脚本 (如Windows启动脚本)
├── docs/               # 项目文档
│   ├── CHANGELOG.md    # 版本更新日志
│   └── ...
├── .gitignore          # Git忽略文件配置
├── requirements.txt    # Python依赖项
├── README.md           # 项目介绍文档
└── ...
```

---

## 开发与贡献

我们欢迎任何形式的贡献，无论是修复Bug、增加新功能还是改进文档。

### 开发环境

```bash
# 安装核心和开发依赖
pip install -r requirements.txt
pip install -e ".[dev]"

# 建议安装 pre-commit 钩子来自动格式化代码
pre-commit install
```

### 贡献流程

1.  **Fork** 本仓库。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将更改推送到分支 (`git push origin feature/AmazingFeature`)。
5.  打开一个 **Pull Request**。

---

## 法律合规指南

本工具的设计考虑了电子证据的法律合规要求，主要参考了 **GB/T 29360-2012** 和 **ISO/IEC 27037:2012** 标准。

-   **真实性与完整性**：通过SHA256哈希算法确保截图内容未被篡改。
-   **可追溯性**：记录详细的元数据，包括时间戳、系统信息、操作员等。
-   **数字签名**：可选的加密模块可以为证据提供数字签名，进一步增强其法律效力。

> **免责声明**: 本工具旨在为电子证据的固定提供技术支持，但其本身不能替代专业的司法鉴定流程。在正式的法律程序中，请咨询合格的司法鉴定专家。

---

## 许可证

本项目采用 [MIT许可证](LICENSE)。
