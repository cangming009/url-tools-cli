# url-tools-cli

[![PyPI version](https://badge.fury.io/py/url-tools-cli.svg)](https://badge.fury.io/py/url-tools-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/cangming/url-tools-cli?style=social)](https://github.com/cangming/url-tools-cli/stargazers)

> B站/YouTube视频字幕提取CLI工具 - 从Bilibili、YouTube、抖音等平台提取视频字幕

## 特性

- 🎬 **多平台支持**: Bilibili、YouTube、抖音
- 📝 **智能字幕选择**: 自动优先中文字幕 (ai-zh > zh-CN > zh-Hans > zh)
- 🔧 **简单易用**: 一行命令提取字幕
- 📦 **开箱即用**: 零配置，自动检测平台
- 🔒 **隐私优先**: 默认使用本地浏览器Cookie，无需分享账号

## 快速开始

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/cangming/url-tools-cli/main/install.sh | bash
```

### 基本用法

```bash
# 提取B站视频字幕
url-tools extract "https://www.bilibili.com/video/BV1GJ411x7h7"

# 提取YouTube视频字幕
url-tools extract "https://www.youtube.com/watch?v=xxxxx"

# 指定输出目录
url-tools extract "URL" --out "./outputs/"

# JSON输出 (适合程序调用)
url-tools extract "URL" --json --quiet
```

## 安装方式

### 方式一: 一键安装脚本 (推荐)

```bash
curl -fsSL https://raw.githubusercontent.com/cangming/url-tools-cli/main/install.sh | bash
```

### 方式二: pip 安装

```bash
pip install url-tools-cli
```

### 方式三: 从源码安装

```bash
git clone https://github.com/cangming/url-tools-cli.git
cd url-tools-cli
pip install -e .
```

### 方式四: Homebrew (macOS)

```bash
brew install url-tools-cli
```

## 使用示例

### 基础命令

```bash
# 提取视频字幕
url-tools extract "https://www.bilibili.com/video/BV1GJ411x7h7"

# 查看帮助
url-tools --help

# 查看完整文档
url-tools full

# 环境检查
url-tools doctor
```

### 高级用法

```bash
# 输出到指定目录
url-tools extract "URL" --out "/path/to/output"

# 静默模式 (适合脚本)
url-tools extract "URL" --quiet

# JSON格式输出 (适合程序调用)
url-tools extract "URL" --json

# 组合使用
url-tools extract "URL" --out "./outputs/" --json --quiet
```

### 在脚本中使用

```bash
#!/bin/bash
# 批量提取视频字幕

URLS=(
    "https://www.bilibili.com/video/BV1GJ411x7h7"
    "https://www.youtube.com/watch?v=xxxxx"
)

for url in "${URLS[@]}"; do
    result=$(url-tools extract "$url" --json --quiet)
    echo "$result"
done
```

## 输出说明

成功提取后，会在输出目录生成两个文件：

| 文件类型 | 说明 |
|---------|------|
| `.srt` | 字幕文件 (带时间戳) |
| `.txt` | 纯文本转录 (无时间戳) |

示例输出：

```
outputs/
├── video_title.srt
└── video_title.txt
```

## 支持的平台

| 平台 | URL 格式 | 状态 |
|------|----------|------|
| Bilibili | bilibili.com/video/... | ✅ 稳定 |
| YouTube | youtube.com/watch?v=... | ✅ 稳定 |
| 抖音 | douyin.com/video/... | ✅ 稳定 |

## 字幕优先级

自动选择最佳字幕，语言优先级：

1. `ai-zh` - AI中文翻译
2. `zh-CN` / `zh-Hans` - 简体中文
3. `zh` - 中文
4. `en` - 英文
5. 其他可用字幕

排除: `danmaku` (弹幕文件)

## 环境要求

- Python 3.12+
- yt-dlp (自动安装)
- ffmpeg (可选，用于视频处理)

### 检查环境

```bash
url-tools doctor
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `URL_TOOLS_OUTPUT` | 输出目录 | `./outputs` |
| `URL_TOOLS_LANGUAGE` | 字幕语言 | `zh` (中文) |
| `URL_TOOLS_COOKIES` | Cookie文件路径 | 自动检测 |

## 故障排除

### 常见问题

**Q: 提示 "No subtitles found"**
- 视频可能没有字幕
- 尝试登录后再提取

**Q: 提示 "412 Request blocked" (B站)**
- B站限流，需要登录
- 使用 `--cookies-from-browser chrome` 参数

**Q: 提示 "Sign in to confirm" (YouTube)**
- YouTube需要认证
- 导出浏览器Cookie后使用

**Q: yt-dlp not found**
```bash
pip install yt-dlp
```

### 获取帮助

```bash
# 查看帮助
url-tools --help

# 查看完整文档
url-tools full

# 环境检查
url-tools doctor
```

## 开发

### 安装开发环境

```bash
make install  # 或 pip install -e ".[dev]"
```

### 运行测试

```bash
make test     # 或 pytest tests/ -v
```

### 代码检查

```bash
make lint     # 或 ruff check src/
make format   # 或 ruff format src/
```

### Makefile 目标

| 目标 | 说明 |
|------|------|
| `make install` | 安装依赖 |
| `make build` | 构建包 |
| `make test` | 运行测试 |
| `make lint` | 代码检查 |
| `make clean` | 清理构建产物 |
| `make publish` | 发布到 PyPI |
| `make publish-test` | 发布到 Test PyPI |
| `make doctor` | 环境检查 |

## 技术栈

- [Typer](https://typer.tiangolo.com/) - CLI 框架
- [Rich](https://github.com/Textualize/rich) - 终端美化
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载/字幕提取

## License

MIT License - see [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！