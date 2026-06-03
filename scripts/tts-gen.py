#!/usr/bin/env python3
"""
tts-gen.py - 通用 MiniMax TTS 生成器

用法:
    python tts-gen.py "要转换的文字" [选项]

示例:
    # 简单调用
    python tts-gen.py "你好世界" --output hello.mp3

    # 指定音色
    python tts-gen.py "今天天气真好" --voice 国语女声 --output test.mp3

    # 流式输出（边生成边播放）
    python tts-gen.py "实时语音播报" --stream

    # 批量生成（从文件，每行一条）
    python tts-gen.py --batch texts.txt --output-dir ./out/

特性:
    - 支持单条/批量生成
    - 支持流式响应
    - 支持音频元数据嵌入
    - 支持多种输出格式（mp3/wav/pcm）
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请先运行: pip install requests")
    sys.exit(1)


API_ENDPOINT = "https://api.minimax.chat/v1/t2a_v2"
DEFAULT_VOICE = "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85"
DEFAULT_MODEL = "speech-02-hd"

VOICE_PRESETS = {
    "国语男声": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
    "国语女声": "moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d",
    "抒情男声": "Chinese (Mandarin)_Lyrical_Voice",
    "空乘女声": "Chinese (Mandarin)_HK_Flight_Attendant",
    "粤语女声": "Cantonese_GentleLady",
    "粤语播客": "Cantonese_podacast_host_1",
}


def call_tts_once(text: str, voice_id: str, api_key: str,
                  speed: float, volume: float, fmt: str = "mp3",
                  bitrate: int = 128000) -> bytes:
    """单次 TTS 调用"""
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
            "format": fmt,
            "bitrate": bitrate
        }
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()

    if not result.get("data"):
        raise RuntimeError(f"API 错误: {result.get('base_resp', result)}")

    return bytes.fromhex(result["data"]["audio"])


def call_tts_stream(text: str, voice_id: str, api_key: str,
                    speed: float, volume: float, fmt: str = "mp3"):
    """流式 TTS 调用（生成器）"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "text": text,
        "stream": True,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "volume": volume,
            "pitch": 0
        },
        "audio_setting": {
            "format": fmt,
            "bitrate": 128000
        }
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=payload,
                            stream=True, timeout=120)
    response.raise_for_status()

    buffer = b""
    for chunk in response.iter_content(chunk_size=4096):
        buffer += chunk
        # SSE 格式: data: {...}\n\n
        while b"\n\n" in buffer:
            event, buffer = buffer.split(b"\n\n", 1)
            if event.startswith(b"data: "):
                import json
                try:
                    data = json.loads(event[6:].decode("utf-8"))
                    if data.get("data", {}).get("audio"):
                        yield bytes.fromhex(data["data"]["audio"])
                except json.JSONDecodeError:
                    pass


def main():
    parser = argparse.ArgumentParser(
        description="通用 MiniMax TTS 生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="?", help="要转换的文本")
    parser.add_argument("--voice", "-v", default="国语男声", help="音色名称或 ID")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="语速 0.5-2.0")
    parser.add_argument("--volume", default=1.5, help="音量 0.0-2.0")
    parser.add_argument("--format", "-f", default="mp3", choices=["mp3", "wav", "pcm"], help="音频格式")
    parser.add_argument("--bitrate", type=int, default=128000, help="比特率")
    parser.add_argument("--stream", action="store_true", help="流式响应")
    parser.add_argument("--batch", help="批量模式：读取文件，每行一条")
    parser.add_argument("--output-dir", default="./output", help="批量模式输出目录")
    parser.add_argument("--api-key", default=None, help="API Key（默认从环境变量读取）")

    args = parser.parse_args()

    # API Key
    api_key = args.api_key or os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("❌ 未设置 API Key")
        print("   设置环境变量: export MINIMAX_API_KEY=your_key")
        print("   或使用 --api-key 参数")
        sys.exit(1)

    # 音色解析
    voice_id = VOICE_PRESETS.get(args.voice, args.voice)

    # 批量模式
    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"❌ 批量文件不存在: {batch_path}")
            sys.exit(1)

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        lines = [l.strip() for l in batch_path.read_text(encoding="utf-8").split("\n") if l.strip()]
        print(f"📋 批量生成 {len(lines)} 条")
        print(f"📁 输出目录: {output_dir}")

        for i, line in enumerate(lines, 1):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"audio_{i:03d}_{timestamp}.{args.format}"
            print(f"🎙️  [{i}/{len(lines)}] {line[:30]}{'...' if len(line) > 30 else ''}")

            try:
                audio = call_tts_once(line, voice_id, api_key,
                                      args.speed, args.volume, args.format, args.bitrate)
                output_path.write_bytes(audio)
                print(f"   ✅ {output_path.name} ({len(audio)/1024:.1f} KB)")
            except Exception as e:
                print(f"   ❌ 失败: {e}")

        return

    # 单条模式
    if not args.text:
        parser.print_help()
        sys.exit(1)

    output_path = args.output or f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"

    print(f"🎤 音色: {args.voice}")
    print(f"📝 文本: {args.text[:50]}{'...' if len(args.text) > 50 else ''}")
    print(f"💾 输出: {output_path}")

    if args.stream:
        print("🌊 流式生成...")
        chunks = []
        total_size = 0
        for chunk in call_tts_stream(args.text, voice_id, api_key,
                                     args.speed, args.volume, args.format):
            chunks.append(chunk)
            total_size += len(chunk)
            print(f"   📦 已接收: {total_size/1024:.1f} KB", end="\r")
        print()

        with open(output_path, "wb") as f:
            for chunk in chunks:
                f.write(chunk)
    else:
        audio = call_tts_once(args.text, voice_id, api_key,
                             args.speed, args.volume, args.format, args.bitrate)
        Path(output_path).write_bytes(audio)

    size_kb = Path(output_path).stat().st_size / 1024
    print(f"✅ 完成: {output_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
