from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from url_tools_cli import __version__
from url_tools_cli.extractor import clean_bilibili_url, detect_platform, extract_subtitles

app = typer.Typer(
    name="url-tools",
    help="B站/YouTube视频字幕提取CLI工具",
)
console = Console()
err_console = Console(stderr=True)


def _print(s: str = "") -> None:
    """Print plain text without Rich formatting."""
    print(s)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Show agent-friendly guide when no subcommand is given."""
    if ctx.invoked_subcommand is not None:
        return

    _print("""url-tools — B站/YouTube视频字幕提取CLI

适用场景：
  • B站视频字幕提取
  • YouTube视频字幕提取
  • 视频转文字/Transcript

最常用命令：

  url-tools extract "https://www.bilibili.com/video/BV1GJ411x7h7"
  url-tools extract "URL" --out "./outputs/"
  url-tools extract "URL" --json --quiet
  url-tools doctor
  url-tools --help

支持平台：
  • B站 (bilibili.com)
  • YouTube (youtube.com, youtu.be)
  • 抖音 (douyin.com)

Agent 规则:
  • 默认使用浏览器Cookie认证 (--cookies-from-browser chrome)
  • 优先提取中文字幕 (ai-zh > zh-CN > zh-Hans > zh > 其他)
  • Agent 自动化调用时默认加 --json --quiet
  • 失败时先运行 url-tools doctor

更多信息:
  url-tools full       完整文档
  url-tools --help     传统命令帮助
  url-tools doctor     环境检查""")


@app.command()
def extract(
    url: str = typer.Argument(..., help="视频URL"),
    out: str = typer.Option("./outputs", "--out", "-o", help="输出目录"),
    json_output: bool = typer.Option(False, "--json", help="JSON输出"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="静默模式"),
) -> None:
    """提取视频字幕"""
    output_path = Path(out)
    output_path.mkdir(parents=True, exist_ok=True)

    platform = detect_platform(url)
    if not quiet:
        console.print(f"[cyan]Platform:[/] {platform}")

    result = extract_subtitles(url, output_dir=str(output_path))

    if result["success"]:
        data = {
            "ok": True,
            "subtitle_path": result["subtitle_path"],
            "transcript_path": result["transcript_path"],
            "platform": platform,
        }
        if json_output:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            console.print(f"[green]✓ 成功！[/]")
            console.print(f"字幕文件: {result['subtitle_path']}")
            console.print(f"文本文件: {result['transcript_path']}")
            with open(result["transcript_path"], "r", encoding="utf-8") as f:
                lines = f.readlines()[:5]
                if lines:
                    console.print("\n[cyan]预览:[/]")
                    for line in lines:
                        console.print(f"  {line.rstrip()}")
    else:
        data = {"ok": False, "error": result["error"]}
        if json_output:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            console.print(f"[red]✗ 失败:[/] {result['error']}")
        raise typer.Exit(1)


@app.command()
def doctor() -> None:
    """检查环境依赖"""
    table = Table(title="url-tools 环境检查")
    table.add_column("检查项", style="cyan")
    table.add_column("状态", style="green")

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python version", python_version)
    table.add_row("url-tools version", __version__)

    import shutil
    ytdlp = shutil.which("yt-dlp")
    if ytdlp:
        table.add_row("yt-dlp", f"OK ({ytdlp})")
    else:
        table.add_row("yt-dlp", "NOT FOUND (pip install yt-dlp)")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        table.add_row("ffmpeg", f"OK ({ffmpeg})")
    else:
        table.add_row("ffmpeg", "NOT FOUND (optional)")

    console.print(table)


@app.command()
def full() -> None:
    """显示完整文档"""
    _print("""
url-tools - B站/YouTube视频字幕提取CLI工具
============================================

概述:
  url-tools 是基于 yt-dlp 的视频字幕提取CLI工具。
  支持 B站、YouTube、抖音等平台的字幕提取。

CLI 命令:
---------

1. url-tools                          基本使用说明
2. url-tools --help                   传统命令帮助
3. url-tools full                     当前完整文档
4. url-tools doctor                   环境检查
5. url-tools extract <URL>            提取字幕

字幕提取:
  url-tools extract "https://www.bilibili.com/video/BV1GJ411x7h7"
  url-tools extract "URL" --out "./outputs/" --json --quiet

参数:
  URL                视频URL（必需）
  --out, -o          输出目录（默认 ./outputs）
  --json             输出JSON结果
  --quiet, -q        静默模式

支持平台:
---------
  • B站 (bilibili.com)
  • YouTube (youtube.com, youtu.be)
  • 抖音 (douyin.com)

字幕优先级:
-----------
  1. ai-zh (AI中文)
  2. zh-CN / zh-Hans (简体中文)
  3. .zh. (通用中文)
  4. zh (中文)
  5. en (英文)
  6. 其他
  排除: danmaku (弹幕文件)

认证:
-----
  默认使用浏览器Cookie认证:
  yt-dlp --cookies-from-browser chrome ...

常见错误:
---------
  • No subtitles found      视频没有字幕
  • 412 Request blocked      B站限流，需要登录
  • yt-dlp not found         pip install yt-dlp
  • Sign in to confirm        YouTube需要认证
""")


if __name__ == "__main__":
    app()