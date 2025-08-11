# 🛠️ 工具目录

本目录包含智能滚动截图工具的各种辅助工具和脚本。

## 📋 工具列表

### 🔍 check_imports.py
**依赖检查工具**
- 检查所有必需的依赖包
- 验证主程序导入
- 提供详细的错误信息

```bash
python tools/check_imports.py
```

### 🔧 debug_run.py
**调试运行工具**
- 提供详细的系统信息
- 逐步检查各个组件
- 包含完整的错误追踪

```bash
python tools/debug_run.py
```

### 🚀 quick_start.py
**快速启动工具**
- 简化的启动流程
- 快速检查关键依赖
- 适合日常使用

```bash
python tools/quick_start.py
```

### 🧪 simple_test.py
**可视化测试工具**
- 图形化测试界面
- 交互式测试流程
- 可直接启动主程序

```bash
python tools/simple_test.py
```

## 🎯 使用建议

### 🔰 新用户
1. 首先运行 `check_imports.py` 检查环境
2. 如有问题，运行 `debug_run.py` 获取详细信息
3. 环境正常后，使用 `quick_start.py` 启动

### 👨‍💻 开发者
1. 使用 `debug_run.py` 进行详细调试
2. 使用 `simple_test.py` 进行可视化测试
3. 开发过程中使用 `check_imports.py` 验证依赖

### 🔧 故障排除
1. 程序无法启动 → `debug_run.py`
2. 依赖问题 → `check_imports.py`
3. 需要可视化测试 → `simple_test.py`
4. 日常使用 → `quick_start.py`

## 📞 获取帮助

如果工具无法解决您的问题，请：
1. 查看 [故障排除指南](../docs_unified/05_故障排除指南.md)
2. 提交 GitHub Issue
3. 查看项目文档

---

**工具版本**: v3.0.6  
**最后更新**: 2024-12-19  
**维护状态**: 活跃维护中