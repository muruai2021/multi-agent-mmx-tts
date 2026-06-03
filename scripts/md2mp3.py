#!/usr/bin/env python3
"""
md2mp3.py - Markdown 口播文案一键转 MP3

用法:
    python md2mp3.py <markdown文件> [选项]

示例:
    # 最简用法（用默认音色）
    python md2mp3.py 口播文案.md

    # 指定音色和输出
    python md2mp3.py 口播文案.md --voice 国语女声 --output ./out/

    # 启用停顿插入（识别 ... 和 ——）
    python md2mp3.py 口播文案.md --insert-pauses

    # 自定义语速音量
    python md2mp3.py 口播文案.md --speed 1.1 --volume 1.3

特性:
    - 自动解析 Frontmatter（voice/speed/volume 配置）
    - 自动跳过 markdown 标题（# ##）
    - 识别停顿符号（... ——）插入静音
    - 长文本自动分段（按 4500 字符切分）
    - 自动合并分段音频
"""

import argparse
import os
import re
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请先运行: pip install requests")
    sys.exit(1)


# ============== 配置 ==============

API_ENDPOINT = "https://api.minimax.chat/v1/t2a_v2"
DEFAULT_VOICE = "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85"
DEFAULT_MODEL = "speech-02-hd"
DEFAULT_SPEED = 1.0
DEFAULT_VOLUME = 1.5
DEFAULT_OUTPUT_DIR = "C:/Claude/wechat/"
MAX_CHARS_PER_REQUEST = 4500  # 留余量，避免触发 5000 上限

VOICE_PRESETS = {
    "国语男声": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
    "国语女声": "moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d",
    "抒情男声": "Chinese (Mandarin)_Lyrical_Voice",
    "空乘女声": "Chinese (Mandarin)_HK_Flight_Attendant",
    "粤语女声": "Cantonese_GentleLady",
    "粤语播客": "Cantonese_podacast_host_1",
}


# ============== Frontmatter 解析 ==============

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 Markdown Frontmatter，返回 (config, 正文)"""
    config = {}
    body = content

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = content[match.end():]
        for line in fm_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                config[key.strip()] = value.strip()

    return config, body


# ============== 文本处理 ==============

def clean_markdown(text: str) -> str:
    """清理 Markdown 标记，保留正文与停顿符号"""
    # 跳过整段标题块（# ## ###）
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    # 跳过代码块
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # 跳过行内代码
    text = re.sub(r"`[^`]+`", "", text)
    # 跳过链接，保留文本
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # 跳过图片
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    # 跳过加粗标记，保留文本
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    # 跳斜体标记，保留文本
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # 多空行合并
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text_by_pauses(text: str, insert_pauses: bool, pause_ms: int = 600):
    """
    将文本按句号/段落切分。
    返回: List[{"text": str, "pause_after_ms": int}]
    """
    if not insert_pauses:
        return [{"text": text, "pause_after_ms": 0}]

    # 按段落切
    paragraphs = text.split("\n\n")
    segments = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # 按句号/问号/感叹号 切
        sentences = re.split(r"([。！？])", para)
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
            sentence = sentence.strip()
            if not sentence:
                continue
            # 判断停顿时长
            pause = pause_ms
            if "..." in sentence or "——" in sentence:
                pause = int(pause_ms * 1.5)
            segments.append({"text": sentence, "pause_after_ms": pause})

    return segments


def split_long_text(text: str, max_chars: int = MAX_CHARS_PER_REQUEST) -> list[str]:
    """将长文本按 max_chars 切分（尽量在段落/句号边界切）"""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    paragraphs = text.split("\n\n")

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            # 单段超长，硬切
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i+max_chars])
                current = ""
            else:
                current = para + "\n\n"

    if current:
        chunks.append(current.strip())

    return chunks


# ============== TTS 调用 ==============

def call_tts(text: str, voice_id: str, api_key: str,
             speed: float = 1.0, volume: float = 1.5) -> bytes:
    """调用 MiniMax TTS API，返回音频二进制数据"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "volume": volume,
            "pitch": 0
        },
        "audio_setting": {
            "format": "mp3",
            "bitrate": 128000
        }
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(f"API HTTP 错误 {response.status_code}: {response.text[:500]}")

    result = response.json()
    if not result.get("data"):
        raise RuntimeError(f"API 返回错误: {result.get('base_resp', result)}")

    return bytes.fromhex(result["data"]["audio"])


def merge_audio_files(audio_paths: list[str], output_path: str):
    """用 ffmpeg 拼接多个 MP3，自动用 concat demuxer"""
    if len(audio_paths) == 1:
        # 只有一个文件，直接复制
        import shutil
        shutil.copy(audio_paths[0], output_path)
        return

    # 检查 ffmpeg
    if subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0:
        print("⚠️  未检测到 ffmpeg，将简单拼接（可能有卡顿）")
        with open(output_path, "wb") as out:
            for p in audio_paths:
                with open(p, "rb") as f:
                    out.write(f.read())
        return

    # 用 ffmpeg concat
    list_file = output_path + ".list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in audio_paths:
            # 转义路径中的单引号
            safe = p.replace("'", "'\\''")
            f.write(f"file '{safe}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path
    ], capture_output=True)

    os.remove(list_file)


def insert_silence(audio_path: str, silence_ms: int, output_path: str):
    """在音频末尾插入静音"""
    if silence_ms <= 0:
        import shutil
        shutil.copy(audio_path, output_path)
        return

    if subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0:
        # 无 ffmpeg，跳过停顿
        import shutil
        shutil.copy(audio_path, output_path)
        return

    subprocess.run([
        "ffmpeg", "-y",
        "-i", audio_path,
        "-af", f"apad=pad_dur={silence_ms/1000}",
        output_path
    ], capture_output=True)


# ============== 主流程 ==============

def main():
    parser = argparse.ArgumentParser(
        description="Markdown 口播文案一键转 MP3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python md2mp3.py 口播文案.md
  python md2mp3.py 口播文案.md --voice 国语女声
  python md2mp3.py 口播文案.md --insert-pauses --output ./output/
        """
    )
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("--voice", "-v", default=None, help="音色名称或 ID（默认从 frontmatter 读取）")
    parser.add_argument("--output", "-o", default=None, help=f"输出目录（默认 {DEFAULT_OUTPUT_DIR}）")
    parser.add_argument("--speed", "-s", type=float, default=None, help="语速 0.5-2.0（默认 1.0）")
    parser.add_argument("--volume", default=None, help="音量 0.0-2.0（默认 1.5）")
    parser.add_argument("--insert-pauses", "-p", action="store_true", help="在 ... 和 —— 处插入静音")
    parser.add_argument("--pause-ms", type=int, default=600, help="停顿毫秒数（默认 600）")
    parser.add_argument("--api-key", default=None, help="MiniMax API Key（默认从环境变量 MINIMAX_API_KEY 读取）")

    args = parser.parse_args()

    # 读取 API Key
    api_key = args.api_key or os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("❌ 未设置 API Key，请通过 --api-key 或环境变量 MINIMAX_API_KEY 提供")
        print("   申请地址: https://platform.minimaxi.com")
        sys.exit(1)

    # 读取 Markdown
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    print(f"📖 读取文件: {input_path}")
    content = input_path.read_text(encoding="utf-8")

    # 解析 frontmatter
    fm_config, body = parse_frontmatter(content)

    # 合并配置
    voice_name = args.voice or fm_config.get("voice", "国语男声")
    voice_id = VOICE_PRESETS.get(voice_name, voice_name)  # 允许直接传 ID
    speed = float(args.speed if args.speed is not None else fm_config.get("speed", DEFAULT_SPEED))
    volume = float(args.volume if args.volume is not None else fm_config.get("volume", DEFAULT_VOLUME))
    insert_pauses = args.insert_pauses or fm_config.get("insert_pauses", "false").lower() == "true"
    pause_ms = int(args.pause_ms)

    print(f"🎤 音色: {voice_name}")
    print(f"⚡ 语速: {speed} | 🔊 音量: {volume}")
    print(f"⏸️  插入停顿: {insert_pauses} ({pause_ms}ms)")

    # 清理 markdown
    text = clean_markdown(body)
    if not text:
        print("❌ 文件内容为空（清理 markdown 后）")
        sys.exit(1)

    print(f"📝 文本长度: {len(text)} 字符")
    print(f"⏱️  预计时长: {len(text) / 240 / speed:.1f} 分钟（按 240字/分 估算）")

    # 切分长文本
    chunks = split_long_text(text)
    print(f"🔪 文本分段: {len(chunks)} 段")

    # 输出路径
    output_dir = Path(args.output or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = input_path.stem + ".mp3"
    output_path = output_dir / output_filename

    # 临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        segment_files = []

        # 逐段生成
        for i, chunk in enumerate(chunks, 1):
            print(f"🎙️  生成第 {i}/{len(chunks)} 段 ({len(chunk)} 字符)...")
            try:
                audio_data = call_tts(chunk, voice_id, api_key, speed, volume)
            except Exception as e:
                print(f"❌ 第 {i} 段生成失败: {e}")
                sys.exit(1)

            seg_path = tmp / f"seg_{i:03d}.mp3"
            seg_path.write_bytes(audio_data)
            segment_files.append(str(seg_path))
            print(f"   ✅ 第 {i} 段完成 ({len(audio_data) / 1024:.1f} KB)")

        # 插入停顿
        if insert_pauses:
            print("⏸️  插入停顿...")
            paused_files = []
            # 重新切分（按句子），用于在每句后插入停顿
            for i, chunk in enumerate(chunks, 1):
                sentences = split_text_by_pauses(chunk, insert_pauses=True, pause_ms=pause_ms)
                sent_files = []
                for j, sent in enumerate(sentences, 1):
                    try:
                        audio_data = call_tts(sent["text"], voice_id, api_key, speed, volume)
                    except Exception as e:
                        print(f"❌ 句子 {i}.{j} 生成失败: {e}")
                        sys.exit(1)
                    s_path = tmp / f"sent_{i:03d}_{j:03d}.mp3"
                    s_path.write_bytes(audio_data)

                    # 在末尾插入停顿
                    if sent["pause_after_ms"] > 0:
                        paused_path = tmp / f"paused_{i:03d}_{j:03d}.mp3"
                        insert_silence(str(s_path), sent["pause_after_ms"], str(paused_path))
                        sent_files.append(str(paused_path))
                    else:
                        sent_files.append(str(s_path))

                # 合并该段的所有句子
                if len(sent_files) > 1:
                    merged_path = tmp / f"para_{i:03d}.mp3"
                    merge_audio_files(sent_files, str(merged_path))
                    paused_files.append(str(merged_path))
                else:
                    paused_files.append(sent_files[0])
            segment_files = paused_files

        # 合并所有段
        print("🔗 拼接最终音频...")
        merge_audio_files(segment_files, str(output_path))

        size_kb = output_path.stat().st_size / 1024
        print("")
        print("=" * 50)
        print(f"✅ 完成！输出文件: {output_path}")
        print(f"📦 文件大小: {size_kb:.1f} KB")
        print(f"⏱️  实际时长: {size_kb / 16 / speed:.1f} 分钟（粗略估算）")
        print("=" * 50)


if __name__ == "__main__":
    main()
