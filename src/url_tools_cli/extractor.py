"""URL视频字幕提取核心模块"""
import json
import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def detect_platform(url: str) -> str:
    """检测URL平台"""
    if "bilibili.com" in url:
        return "bilibili"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "douyin.com" in url:
        return "douyin"
    return "unknown"


def clean_bilibili_url(url: str) -> str:
    """清理B站URL，提取标准视频页面"""
    # 移除 ?p=xxx 等参数
    url = re.sub(r'\?.*$', '', url)
    # 提取 BV 号
    bv_match = re.search(r'BV\w+', url)
    if bv_match:
        return f"https://www.bilibili.com/video/{bv_match.group()}"
    # 已经是标准格式
    if "/video/" in url:
        return url
    return url


def extract_subtitles(url: str, output_dir: str = "./outputs", use_browser_cookies: bool = True) -> dict:
    """
    提取视频字幕

    Returns:
        dict: {
            "success": bool,
            "subtitle_path": str,
            "transcript_path": str,
            "error": str | None
        }
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 清理URL
    platform = detect_platform(url)
    if platform == "bilibili":
        clean_url = clean_bilibili_url(url)
    else:
        clean_url = url

    logger.info(f"Extracting from: {clean_url}")

    # 构建 yt-dlp 命令
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "zh.*,en.*,ai-zh,ai-en,zh,en,all",
        "--sub-format", "srt/vtt/json/best",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
    ]

    if use_browser_cookies:
        cmd.extend(["--cookies-from-browser", "chrome"])

    cmd.append(clean_url)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            logger.error(f"yt-dlp failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "subtitle_path": None,
                "transcript_path": None
            }

        # 查找字幕文件
        subtitle_files = list(output_path.glob("*.srt")) + list(output_path.glob("*.vtt")) + list(output_path.glob("*.json"))

        # 优先选择中文字幕
        chinese_sub = None
        for f in subtitle_files:
            if "ai-zh" in f.name or "zh-CN" in f.name or "zh-Hans" in f.name:
                chinese_sub = f
                break
        if not chinese_sub:
            for f in subtitle_files:
                if ".zh." in f.name or f.name.endswith(".zh.srt"):
                    chinese_sub = f
                    break
        if not chinese_sub:
            for f in subtitle_files:
                if "zh" in f.name and "danmaku" not in f.name:
                    chinese_sub = f
                    break

        target_sub = chinese_sub or (subtitle_files[0] if subtitle_files else None)

        if not target_sub:
            return {
                "success": False,
                "error": "No subtitles found",
                "subtitle_path": None,
                "transcript_path": None
            }

        # 读取并清洗字幕
        with open(target_sub, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        cleaned_text = clean_subtitle_text(raw_text)

        # 生成 transcript
        transcript_path = output_path / "transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        return {
            "success": True,
            "subtitle_path": str(target_sub),
            "transcript_path": str(transcript_path),
            "error": None
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Subtitle extraction timed out after 300s",
            "subtitle_path": None,
            "transcript_path": None
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "yt-dlp not found. Install: pip install yt-dlp",
            "subtitle_path": None,
            "transcript_path": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "subtitle_path": None,
            "transcript_path": None
        }


def clean_subtitle_text(text: str) -> str:
    """清洗字幕文本"""
    import re
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除时间戳
    text = re.sub(r'\[?\d{2}:\d{2}:\d{2}\]?', '', text)
    text = re.sub(r'\[?\d{2}:\d{2}\]?', '', text)
    # 移除 SRT 时间线
    text = re.sub(r'^,\d+\s*-->\s*,.+$', '', text, flags=re.MULTILINE)
    # 移除纯数字行
    text = re.sub(r'^[\d,]+$', '', text, flags=re.MULTILINE)
    # 移除 WEBVTT 头
    text = re.sub(r'^WEBVTT\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^NOTE\s+.*$', '', text, flags=re.MULTILINE)
    # 清理空白
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)