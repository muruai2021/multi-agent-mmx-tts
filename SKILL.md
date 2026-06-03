---
name: multi-agent-mmx-tts
description: Use when 用户需要 MiniMax TTS 语音合成，包括 API Key 申请、Voice ID 获取、音频生成、或调用 MiniMax API 进行文字转语音。默认使用 moss_audio 国语男声，音量 1.5，输出到 C:\Claude\wechat\。同时提供"反 AI 味"口播脚本写手指南与 MD→MP3 一键转换工具。
version: 1.2.0
author: Muru AI
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tts, minimax, voice, audio, speech-synthesis, script-writer, wechat-mp3]
    related_skills: [mmx-tts-config, multi-agent-wechat]
  default_voice: moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85
  default_volume: 1.5
  default_output: C:\Claude\wechat\
---

# MiniMax TTS 技能

> MiniMax 语音合成 API 一站式配置与使用指南

## Overview

本 Skill 提供 MiniMax TTS 服务的完整配置流程，包括 API Key 申请、音色选择、参数配置，以及代码调用示例。

**默认配置：**
- 音色：`moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85`（国语男声）
- 音量：1.5
- 输出目录：`C:\Claude\wechat\`

**计费说明：** MiniMax 提供免费额度（新用户有赠送），超出后按量付费。请在 [控制台](https://platform.minimaxi.com) 查看用量。

## When to Use

**触发词（满足任一即可）：**
- "MiniMax TTS"
- "MiniMax 语音"
- "文字转语音"
- "语音合成"
- "申请 API Key"
- "配置音色"
- "/tts"
- "mmx-tts"（旧名称，兼容）
- "multi-agent-mmx-tts"（新名称）
- "口播脚本" / "口播文案" / "写脚本" / "脚本写手"
- "MD 转 MP3" / "md2mp3"
- "反 AI 味" / "人味" / "不像 AI 写的"
- "停顿插入" / "插入静音"

**适用场景：**
- 文本转语音配音
- 口播文案生成（含"反 AI 味"人味写作）
- 有声内容制作
- 语音助手配置
- 微信公众号口播 MP3 一键生成
- Markdown 口播稿 → MP3 批量转换

## 快速配置

### 步骤 1：访问 MiniMax 开放平台

**国内版官网：** https://platform.minimaxi.com

> ⚠️ 注意：请使用国内版（minimaxi.com），不是国际版（minimax.io）

### 步骤 2：注册/登录账号

支持以下注册方式：
- 📱 手机号注册（推荐）
- 微信扫码
- 账号密码登录

### 步骤 3：获取 API Key

1. 登录后进入控制台
2. 在左侧菜单找到「API 管理」或「我的 API Key」
3. 点击「创建 API Key」
4. 复制生成的 API Key

## 可用音色列表

### 国语/普通话

| 音色名称 | Voice ID | 风格 |
|----------|----------|------|
| 国语男声 | `moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85` | 清晰专业 |
| 国语女声 | `moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d` | 清晰自然 |
| 抒情男声 | `Chinese (Mandarin)_Lyrical_Voice` | 抒情悠扬 |
| 空乘女声 | `Chinese (Mandarin)_HK_Flight_Attendant` | 专业沉稳 |

### 粤语

| 音色名称 | Voice ID | 说明 |
|----------|----------|------|
| 粤语女声 | `Cantonese_GentleLady` | 温和亲切 |
| 粤语播客 | `Cantonese_podacast_host_1` | 播客风格 |

> 💡 其他语言音色请查看 [官方文档](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)

## API 调用示例

### Node.js 调用（推荐）

```javascript
const https = require('https');
const fs = require('fs');

const apiKey = process.env.MINIMAX_API_KEY;
const text = fs.readFileSync('C:/Claude/wechat/MP3/content.txt', 'utf8');

const postData = JSON.stringify({
  model: 'speech-02-hd',
  text: text,
  stream: false,
  voice_setting: {
    voice_id: 'moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85',
    speed: 1.0,
    volume: 1.5
  },
  audio_setting: {
    format: 'mp3',
    bitrate: 128000
  }
});

const options = {
  hostname: 'api.minimax.chat',
  port: 443,
  path: '/v1/t2a_v2',
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    const result = JSON.parse(data);
    if (result.data) {
      const buffer = Buffer.from(result.data.audio, 'hex');
      fs.writeFileSync('C:/Claude/wechat/MP3/output.mp3', buffer);
      console.log('✅ 音频已生成');
    } else {
      console.error('错误:', result.base_resp);
    }
  });
});

req.write(postData);
req.end();
```

### Python 调用

```python
import requests
import os

API_KEY = os.environ.get('MINIMAX_API_KEY')
VOICE_ID = 'moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85'
TEXT = "要转换的文本内容"

url = "https://api.minimax.chat/v1/t2a_v2"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "speech-02-hd",
    "text": TEXT,
    "stream": False,
    "voice_setting": {
        "voice_id": VOICE_ID,
        "speed": 1.0,
        "volume": 1.5
    },
    "audio_setting": {
        "format": "mp3"
    }
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    result = response.json()
    audio_data = bytes.fromhex(result['data']['audio'])
    with open('C:/Claude/wechat/MP3/output.mp3', 'wb') as f:
        f.write(audio_data)
    print("音频已生成")
```

### cURL 调用

```bash
curl -X POST "https://api.minimax.chat/v1/t2a_v2" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "speech-02-hd",
    "text": "要转换的文本内容",
    "voice_setting": {
      "voice_id": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
      "speed": 1.0,
      "volume": 1.5
    },
    "audio_setting": {
      "format": "mp3"
    }
  }' \
  -o output.mp3
```

## 参数说明

### voice_setting

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| voice_id | string | - | 音色 ID（必填） |
| speed | float | 1.0 | 语速 0.5-2.0 |
| volume | float | 1.0 | 音量 0.0-2.0 |
| pitch | int | 0 | 音调 -12~12 |

### audio_setting

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| format | string | mp3 | 音频格式：mp3/wav/pcm |
| bitrate | int | 128000 | 比特率 |

## 常见问题

### Q: API Key 申请需要付费吗？
A: MiniMax 提供免费额度，新用户有赠送。超出后按量付费，请在控制台查看用量。

### Q: 音频生成有长度限制吗？
A: 单次请求文本建议不超过 5000 字符。

### Q: 支持哪些语言？
A: 支持中文（国语、粤语）、英文、日文等，具体可用地音色请查看 [官方文档](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)。

### Q: 音频返回的是什么格式？
A: API 返回 hex 编码的二进制数据，需要用 `Buffer.from(audio, 'hex')` 解码。

## 目录结构

```
multi-agent-mmx-tts/
├── SKILL.md                  ← 主入口
├── references/
│   ├── voice-list.md          ← 完整音色列表
│   ├── api-reference.md       ← API 参考文档
│   └── script-writer.md       ← 口播脚本写手指南（反 AI 味）
└── scripts/
    ├── md2mp3.py             ← MD → MP3 一键转换（含停顿插入）
    └── tts-gen.py            ← 通用 TTS 生成器（单条/批量/流式）
```

---

## 🆕 脚本写手模块（v1.2 新增）

### 解决什么问题？

市面上的 TTS 工具只能"念稿"。但**写出口播稿**这件事，更难。

AI 写的稿子一听就像 AI：排比堆砌、空洞比喻、宏大叙事、总结升华。听众听 5 秒就划走。

本模块专注于**写出口播稿**这件事，详见 [`references/script-writer.md`](references/script-writer.md)。

### 核心内容

- **❌ 反 AI 味 10 条铁律**：禁用词、禁用结构、禁用修辞清单
- **🎣 10 种钩子模板**：颠覆认知、痛点直击、反差冲击、悬念等
- **🎙️ 人味细节注入**：语气词、停顿符号、自我纠正、半截话
- **📏 节奏与时长控制**：字数/时长换算、信息密度建议
- **✍️ 案例对照**：把 AI 味原稿改写为人味版
- **📋 写前自检清单**：10 项必过项
- **🎯 四种文体配方**：科普、故事、干货、情感

### 何时使用

当用户说：
- "帮我写个口播稿"
- "这次要写得像人话，不要 AI 味"
- "开头要吸引人"
- "加点停顿、加点细节"
- "我想录个播客/视频"

---

## 🆕 配套工具脚本（v1.2 新增）

### 1. `md2mp3.py` - Markdown 口播稿一键转 MP3

**用法：**
```bash
# 最简用法
python md2mp3.py 口播文案.md

# 指定音色和输出目录
python md2mp3.py 口播文案.md --voice 国语女声 --output ./out/

# 启用停顿插入（识别 ... 和 —— 自动插入静音）
python md2mp3.py 口播文案.md --insert-pauses

# 使用 frontmatter 配置
python md2mp3.py 口播文案.md   # 自动读取 markdown 顶部的 YAML 配置
```

**支持 Markdown Frontmatter：**
```markdown
---
voice: 国语男声
speed: 1.0
volume: 1.5
insert_pauses: true
pause_ms: 600
---

# 这是标题（不读出）

正文会读出。可以 ... 表示停顿，用 —— 表示强调。
```

**特性：**
- ✅ 自动跳过 markdown 标题/代码块/链接标记
- ✅ 长文本自动分段（4500 字符/段）
- ✅ 识别停顿符号（`...` `——`）插入静音
- ✅ 自动合并分段音频（需 ffmpeg）
- ✅ 默认输出到 `C:\Claude\wechat\`

### 2. `tts-gen.py` - 通用 TTS 生成器

**用法：**
```bash
# 单条
python tts-gen.py "你好世界" --output hello.mp3

# 批量（从文件，每行一条）
python tts-gen.py --batch texts.txt --output-dir ./out/

# 流式响应
python tts-gen.py "实时播报" --stream

# 指定音色格式
python tts-gen.py "测试" --voice 国语女声 --format wav --speed 1.2
```

**特性：**
- ✅ 单条/批量/流式三种模式
- ✅ 多格式输出（mp3/wav/pcm）
- ✅ 自定义语速/音量/比特率
- ✅ 自动时间戳命名（避免覆盖）

### 安装依赖

```bash
pip install requests
# 可选（用于音频拼接和停顿插入）
# Windows: 下载 ffmpeg 并加入 PATH
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

---

## 🔗 与 wechat MP3 项目集成

本 Skill 默认输出目录为 `C:\Claude\wechat\`，与现有口播项目天然兼容。

**典型工作流：**

```
1. 选题（multi-agent-wechat skill）
   ↓
2. 用本 Skill 的"脚本写手"模块写口播稿
   ↓
3. 写入 C:\Claude\wechat\MP3\项目名\口播文案.md
   ↓
4. 运行 md2mp3.py 一键生成同名 MP3
   ↓
5. 发布到公众号 / 视频号 / 抖音
```

## 验证清单

- [x] API Key 已配置在 `settings.json`
- [x] 默认音色：moss_audio 国语男声
- [x] 默认音量：1.5
- [x] 输出目录：C:\Claude\wechat\
- [ ] 测试播放验证

## 输出目录

**默认输出路径：** `C:\Claude\wechat\`

生成的文件自动保存到此目录。
