# Makefile for Smart Screenshot Tool

.PHONY: help install install-dev test lint format clean build docs run

# 默认目标
help:
	@echo "Smart Screenshot Tool - 可用命令:"
	@echo ""
	@echo "  install      安装项目依赖"
	@echo "  install-dev  安装开发依赖"
	@echo "  test         运行测试"
	@echo "  lint         代码检查"
	@echo "  format       代码格式化"
	@echo "  clean        清理临时文件"
	@echo "  build        构建项目"
	@echo "  docs         生成文档"
	@echo "  run          运行主程序"
	@echo ""

# 安装依赖
install:
	pip install -r config/requirements.txt

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# 测试
test:
	python -m pytest tests/ -v
	@echo "✅ 测试完成"

test-cov:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "✅ 测试覆盖率报告已生成"

# 代码质量
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/
	@echo "✅ 代码检查完成"

format:
	black src/ tests/
	isort src/ tests/
	@echo "✅ 代码格式化完成"

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo "✅ 清理完成"

# 构建
build: clean
	python -m build
	@echo "✅ 构建完成"

# 文档
docs:
	@echo "📚 文档位置:"
	@echo "  主文档: README.md"
	@echo "✅ 文档导航完成"

# 运行
run:
	python src/main.py

# 快速开始
quick-start:
	python tools/quick_start.py

# 性能测试
perf-test:
	python tests/test_performance.py

# 检查代码合规性
compliance-check: lint test
	@echo "✅ 代码合规性检查完成"

# 发布准备
release-prep: format lint test build
	@echo "✅ 发布准备完成"

# 安装pre-commit钩子
setup-hooks:
	pre-commit install
	@echo "✅ Git钩子安装完成"