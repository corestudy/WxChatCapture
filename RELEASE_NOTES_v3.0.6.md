# v3.0.6 — 单文档简化版 + 入口修复 + 录屏增强

## 摘要
- 单文档入口：仓库首页 README 即简明使用文档，默认只需阅读一页即可上手
- 稳定性/可发布性改进：入口点 main() 修复、构建配置标准化、版本一致性
- 使用体验提升：新增界面示意图，快速传达核心操作

## 变更详情

### 新增
- 录屏功能体验完善：界面中支持选定区域/全屏，支持设置 FPS（10–30），MP4 输出
- README 顶部新增徽章（Python/OS/License/Version）
- 新增界面示意图 images/overview.svg，帮助快速理解操作流程
- 新增 LICENSE（MIT）

### 变更
- 单文档策略：将简明使用说明合并至根 README，删除 docs_unified/README.md，修复仓库内所有相关引用
- 入口点修复：src/main.py 新增 main() 函数，pyproject 脚本入口 smart-screenshot = "src.main:main" 可用
- 构建配置标准化：将 pyproject.toml 移至仓库根；设置 setuptools src 布局（package-dir={"" : "src"}）
- MANIFEST.in 调整：包含 docs_unified/*.md 与 images/*.svg；打包内容更清晰
- Makefile 调整：install 使用 config/requirements.txt；docs 目标指向 README.md；quick-start 指向 tools/quick_start.py
- Windows 脚本修复：scripts/run_simple.bat 去除硬编码路径，改为 python tools\simple_test.py
- 版本一致性：统一为 v3.0.6（src/__init__.py、src/main.py、src/utils.py、src/config.py、tests/__init__.py）

### 修复
- 修复 README 中失效链接，默认导航到根 README
- 修复历史报告中的文档中心引用，避免 docs_unified/README.md 死链
- 解决入口脚本与 pyproject 控制台入口不匹配导致的无法启动问题

## 兼容性
- 支持 Windows 10/11
- 需要 Python 3.7+
- 依赖见 requirements.txt（指向 config/requirements.txt）

## 安装/升级
### 首次安装
```bash
pip install -r requirements.txt
python src/main.py
# 或
smart-screenshot
```

### 升级
```bash
git pull
pip install -r requirements.txt
```

## 已知注意事项
- GUI 相关测试（tests/test_ui.py 等）适合本地手工验证，CI 环境可能需要跳过或使用 xvfb/禁用主循环
- 屏幕自动化依赖桌面环境权限，服务器或无头环境请勿运行 GUI 程序

## 致谢
感谢使用与反馈！如遇问题请在 Issues 中附上系统版本、Python 版本和简要复现步骤。
