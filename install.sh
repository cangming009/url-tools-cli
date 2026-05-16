#!/bin/bash
#
# url-tools-cli 一键安装脚本
# 支持 macOS, Linux, Windows (via Git Bash/WSL)
#

set -e

REPO="cangming/url-tools-cli"
INSTALL_DIR="${HOME}/.local/bin"
BIN_NAME="url-tools"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# 检测架构
detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)
            echo "amd64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l)
            echo "armv7"
            ;;
        *)
            echo "amd64"
            ;;
    esac
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取最新版本
get_latest_version() {
    local version
    version=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name"' | sed -E 's/.*"tag_name": "v?([^"]+)".*/\1/')
    echo "${version:-latest}"
}

# 下载并安装
install_binary() {
    local os="$1"
    local arch="$2"
    local version="$3"

    log_info "正在下载 url-tools-cli v${version} for ${os}-${arch}..."

    # 创建临时目录
    local tmp_dir
    tmp_dir=$(mktemp -d)
    trap "rm -rf ${tmp_dir}" EXIT

    # 下载文件
    local download_url="https://github.com/${REPO}/releases/download/v${version}/url-tools-cli-${version}-${os}-${arch}.tar.gz"
    local archive_file="${tmp_dir}/url-tools-cli.tar.gz"

    if ! curl -L -o "${archive_file}" "${download_url}"; then
        log_error "下载失败，请检查网络连接或版本是否存在"
        exit 1
    fi

    # 解压
    log_info "正在安装..."
    mkdir -p "${INSTALL_DIR}"
    tar -xzf "${archive_file}" -C "${tmp_dir}"

    # 移动二进制文件
    local binary_path
    binary_path=$(find "${tmp_dir}" -name "${BIN_NAME}" -type f 2>/dev/null | head -1)
    if [ -z "${binary_path}" ]; then
        binary_path=$(find "${tmp_dir}" -name "url-tools*" -type f 2>/dev/null | head -1)
    fi

    if [ -z "${binary_path}" ]; then
        log_error "解压后未找到可执行文件"
        exit 1
    fi

    mv "${binary_path}" "${INSTALL_DIR}/${BIN_NAME}"
    chmod +x "${INSTALL_DIR}/${BIN_NAME}"

    log_info "安装成功！"
}

# 使用 pip 安装
install_pip() {
    log_info "使用 pip 安装..."

    if command_exists pip3; then
        pip3 install --user url-tools-cli
    elif command_exists pip; then
        pip install --user url-tools-cli
    else
        log_error "未找到 pip，请先安装 Python"
        exit 1
    fi

    # 确保用户路径在 PATH 中
    local user_bin
    user_bin=$(python3 -c "import site; print(site.getuserbase() + '/bin')" 2>/dev/null || echo "")
    if [ -n "${user_bin}" ] && [ -d "${user_bin}" ]; then
        if [[ ":$PATH:" != *":${user_bin}:"* ]]; then
            log_warn "请确保 ${user_bin} 在您的 PATH 中"
            export PATH="${PATH}:${user_bin}"
        fi
    fi

    log_info "安装完成！运行 'url-tools --help' 开始使用"
}

# 主安装函数
main() {
    local os=$(detect_os)
    local arch=$(detect_arch)

    echo "=========================================="
    echo "  url-tools-cli 一键安装脚本"
    echo "=========================================="
    echo ""

    # 检查是否已有 url-tools
    if command_exists url-tools; then
        local current_version
        current_version=$(url-tools --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
        log_info "检测到已安装 url-tools-cli v${current_version}"
        read -p "是否要重新安装？ [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi

    log_info "检测到系统: ${os} (${arch})"

    # 询问安装方式
    echo ""
    echo "请选择安装方式:"
    echo "  1) 从源码安装 (推荐，需要 Python 3.12+)"
    echo "  2) 尝试下载预编译二进制 (实验性)"
    echo ""
    read -p "请输入选择 [1]: " choice

    case "${choice}" in
        2)
            local version
            version=$(get_latest_version)
            install_binary "${os}" "${arch}" "${version}"
            ;;
        *)
            install_pip
            ;;
    esac

    # 验证安装
    echo ""
    if command_exists url-tools; then
        log_info "验证安装..."
        url-tools --version 2>/dev/null || url-tools --help | head -5
    else
        echo ""
        log_warn "安装完成但 url-tools 命令不可用。"
        log_warn "请将安装目录添加到 PATH 环境变量："
        echo ""
        echo "  # 对于 bash:"
        echo "  echo 'export PATH=\"\${HOME}/.local/bin:\${PATH}\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo ""
        echo "  # 对于 zsh:"
        echo "  echo 'export PATH=\"\${HOME}/.local/bin:\${PATH}\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
        echo ""
    fi

    echo ""
    log_info "安装完成！运行 'url-tools --help' 查看帮助"
}

# 检查依赖
check_dependencies() {
    if ! command_exists curl; then
        log_error "curl 未安装，请先安装 curl"
        exit 1
    fi
}

check_dependencies
main