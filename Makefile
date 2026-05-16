# Makefile for url-tools-cli

.PHONY: help install build test lint clean publish publish-test test-venv check

# 默认目标
help:
	@echo "url-tools-cli - B站/YouTube视频字幕提取CLI工具"
	@echo ""
	@echo "可用目标:"
	@echo "  install         安装项目依赖"
	@echo "  build           构建/编译项目"
	@echo "  test            运行测试"
	@echo "  lint            代码检查"
	@echo "  clean           清理构建产物"
	@echo "  publish         发布到 PyPI"
	@echo "  publish-test    发布到 Test PyPI"
	@echo "  check           运行所有检查"
	@echo "  doctor          环境检查"

# 安装依赖
install:
	@echo "安装依赖..."
	@pip install -e ".[dev]"

# 构建
build:
	@echo "构建项目..."
	@pip install build
	@python -m build

# 测试
test:
	@echo "运行测试..."
	@python -m pytest tests/ -v --tb=short

# 代码检查
lint:
	@echo "运行代码检查..."
	@python -m ruff check src/

# 格式化代码
format:
	@echo "格式化代码..."
	@python -m ruff format src/

# 清理
clean:
	@echo "清理构建产物..."
	@rm -rf build/ dist/ *.egg-info/ src/*.egg-info/ .pytest_cache/ .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "清理完成"

# 环境检查
doctor:
	@echo "环境检查..."
	@python -c "import sys; print(f'Python: {sys.version}')"
	@pip show url-tools-cli >/dev/null 2>&1 && echo "url-tools-cli: 已安装" || echo "url-tools-cli: 未安装"
	@python -c "import typer; print('typer: OK')"
	@python -c "import rich; print('rich: OK')"
	@python -c "import yt_dlp; print('yt-dlp: OK')"

# 发布到 Test PyPI
publish-test:
	@echo "发布到 Test PyPI..."
	@pip install build twine
	@python -m build
	@twine upload --repository testpypi dist/*

# 发布到 PyPI
publish:
	@echo "发布到 PyPI..."
	@pip install build twine
	@python -m build
	@twine upload dist/*

# 运行所有检查
check: lint test

# 创建虚拟环境
venv:
	@python3 -m venv .venv
	@echo "虚拟环境已创建，运行 'source .venv/bin/activate' 激活"

# 检查包完整性
check-package:
	@echo "检查包完整性..."
	@pip install -e ".[dev]"
	@python -c "import url_tools_cli; print(f'version: {url_tools_cli.__version__}')"
	@url-tools --version