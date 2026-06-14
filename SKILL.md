---
name: multi-agent-mmx-tts
description: Use when 用户需要 MiniMax TTS 语音合成、Edge TTS 兜底、字幕轨生成（SRT/VTT/JSON）、口播稿反 AI 味写作。**核心流程**：口播稿 → GATE1 审定 → TTS+字幕 → 直接输出 MP3+SRT+VTT。**硬约束 2 条**：① GATE 1 必过 ② 不虚构数字/场景/人物。
version: 2.0.0
author: Muru AI
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tts, minimax, edge-tts, voice, audio, speech-synthesis, subtitle, srt, vtt, script-writer, wechat-mp3, gate-review, no-fabrication]
    related_skills: [mmx-tts-config, multi-agent-wechat-html, multi-agent-html-media]
  default_voice: moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85
  default_volume: 1.5
  default_output_dir: ./output
---

# MiniMax TTS 技能

> 核心理念：**一条流水线，从口播稿到 MP3 + 字幕文件，无需手动拼接。**
> 口播稿经过 GATE 审定、TTS 生成、字幕对齐，直接输出 MP3 + SRT + VTT + JSON 时间戳。

**计费说明：** MiniMax 提供免费额度（新用户有赠送），超出后按量付费。请在 [控制台](https://platform.minimaxi.com) 查看用量。

## When to Use

**触发词（满足任一即可）：**
- "MiniMax TTS" / "MiniMax 语音" / "文字转语音" / "语音合成"
- "申请 API Key" / "配置音色" / "/tts"
- "口播脚本" / "口播文案" / "写脚本" / "脚本写手"
- "MD 转 MP3" / "md2mp3"
- "反 AI 味" / "人味" / "不像 AI 写的"
- "停顿插入" / "插入静音"
- "生成字幕" / "SRT 字幕" / "VTT 字幕" / "带字幕" / "字幕轨" / "加字幕"
- "TTS+字幕" / "字幕对齐"
- "GATE 1 审定" / "防虚构"

**排除词（引导到子模块）：**
- "只要字幕" / "只生成 SRT/VTT" → 直接用 `SubsGen.py`
- "只要 TTS" / "不要字幕" → 用 `tts-gen.py`
- "只要 MP3" / "只转换文字" → 用 `md2mp3.py`

**适用场景：**
- 文本转语音配音
- 口播文案生成（含"反 AI 味"人味写作）
- 有声内容制作
- 字幕轨生成（SRT/VTT/JSON）

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
├── SKILL.md                    ← 主入口
├── references/
│   ├── voice-list.md           ← 完整音色列表
│   ├── api-reference.md        ← API 参考文档
│   └── script-writer.md       ← 口播脚本写手指南（反 AI 味）
└── scripts/
    ├── md2mp3.py              ← MD → MP3 一键转换（含停顿插入）
    ├── tts-gen.py             ← 通用 TTS 生成器（单条/批量/流式，自动 Edge TTS 兜底）
    ├── tts-with-subs.py       ← TTS + 字幕一键生成（SRT/VTT/JSON）
    └── SubsGen.py             ← 字幕生成模块（切句/时间戳/格式导出）
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

## 🆕 字幕功能

### 解决什么问题？

TTS 只能"念稿"，但**视频里要显示字幕**——尤其是抖音/视频号/公众号视频，字幕是标配。

本模块在生成 MP3 的同时，自动生成**逐句对齐的字幕轨**，支持：
- **SRT** —— 通用字幕格式，几乎所有播放器都支持
- **WebVTT** —— HTML5 `<track>` 标准，可直接挂到 `<video>` / `<audio>` 标签
- **JSON** —— 时间戳数据，用于自定义前端（如：卡拉 OK 式逐字高亮）

### 工作原理

```
1. 文本按标点切分为字幕句(默认 6-18 字/句)
2. 单次 TTS 调用生成整段 MP3(省 RPM 配额)
3. ffprobe 探测 MP3 真实时长
4. 按字数+停顿符估算每句时长
5. 归一化到真实音频时长 → 生成 SRT / VTT / JSON
```

**为什么这样设计？** 逐句调用 TTS 虽然时间戳精确,但会触发 MiniMax 的 RPM 速率限制。**单次 TTS + 归一化**在精度(±0.3-1s)与稳定性之间取得平衡,适合绝大多数口播场景。

### 用法

**方式 1: 独立字幕工具** `tts-with-subs.py`

```bash
# 单条 + SRT + VTT
python tts-with-subs.py "你好世界" --output hello --srt --vtt

# MD 文件 → MP3 + 字幕
python tts-with-subs.py 口播文案.md --md --output video --all-subs

# 批量
python tts-with-subs.py --batch texts.txt --output-dir ./out/ --srt

# 已有音频,只生成字幕(免 API 调用)
python tts-with-subs.py 口播文案.md --md --audio-only 已有.mp3 --srt --vtt
```

**方式 2: MD→MP3 一体化** `md2mp3.py`(增强)

```bash
# 原有功能保留,新增 --srt / --vtt / --segments-json
python md2mp3.py 口播文案.md --srt --vtt
# 输出: 口播文案.mp3 + 口播文案.srt + 口播文案.vtt
```

**方式 3: 通用 TTS** `tts-gen.py`(增强)

```bash
# 新增 --srt / --vtt / --json 参数
python tts-gen.py "你好" --srt --vtt --output hello
```

### 输出文件

| 文件 | 用途 |
|------|------|
| `xxx.mp3` | 音频 |
| `xxx.srt` | SRT 字幕(通用播放器) |
| `xxx.vtt` | WebVTT 字幕(HTML5 `<track>`) |
| `xxx.segments.json` | JSON 时间戳(自定义集成) |

### SRT 格式示例

```srt
1
00:00:00,000 --> 00:00:02,500
你可能不信

2
00:00:02,500 --> 00:00:06,000
我一个朋友差点把合同改错了
```

### WebVTT 格式示例

```vtt
WEBVTT

00:00:00.000 --> 00:00:02.500
你可能不信

00:00:02.500 --> 00:00:06.000
我一个朋友差点把合同改错了
```

### 在 HTML 视频中使用

```html
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="subtitles" src="video.vtt" srclang="zh" label="中文" default>
</video>

<!-- 或音频 + 字幕 -->
<audio controls>
  <source src="audio.mp3" type="audio/mpeg">
</audio>
<video ...> <!-- WebVTT 也可用于 audio 元素的 track -->
```

### 在 ffmpeg 中烧录硬字幕

```bash
ffmpeg -i audio.mp3 -i subtitles.srt -c copy -c:s mov_text output.mp4
# 或烧录为画面(需要视频流):
ffmpeg -i bg.mp4 -i audio.mp3 -i subtitles.srt \
  -filter_complex "[0:v][2:s]overlay" -shortest output.mp4
```

### 字幕句切分规则

- 主切分: `。！？` 等中英文句末标点
- 太短合并: 不足 6 字与下一句合并
- 太长二次切: 按 `,;:` 切(> 18 字时)
- 仍过长强制切: 按 18 字硬切
- 停顿符加成: `...` +0.5s, `——` +0.3s, `,;:` +0.15s

可通过 `--min-chars` / `--max-chars` 自定义。

### 与本仓库其他 Skill 集成

```
multi-agent-mmx-tts  (生成 MP3 + 字幕)
       ↓
multi-agent-html-media (H5 视频页面)
       ↓ 挂载 VTT
   用户播放 → 音频 + 同步字幕
```

## 验证清单

- [x] API Key 已配置在环境变量 `MINIMAX_API_KEY`
- [x] 默认音色：moss_audio 国语男声
- [x] 默认音量：1.5
- [ ] 测试播放验证

---

## 🚨 硬约束（2 条，必须死守）

| # | 硬约束 | 触发时机 | 触发动作 |
|---|--------|----------|----------|
| **1** | **口播文件必须经人工审核才能进入下一步** | Phase 0.1 完成后 | 进入 TTS 之前必须等人类回复 `OK / 通过 / 继续`；未通过 → 重写或修改后再审定 |
| **2** | **不虚构数字/场景/人物** | 全程 | TTS 内容与字幕不对齐 |

### 硬约束验证机制

**约束 #1 验证**：
- GATE 1 审核申请必须附带用户显式确认
- 用户回复「A」后，AI 必须等待用户确认「通过」或等效表述
- 无法识别回复时，AI 追问「请明确回复 A、B 或 C」

**约束 #2 验证**：
- 自检清单第 3 项升级为：「数字有具体来源 / 场景可验证 / 人物非虚构」
- 口播稿中的数字必须来自可靠举证（我见过/我朋友说/数据显示）

### 硬约束 1 详解：口播审核（必须先停下）

**触发**：Phase 0.1 写完口播稿后，**不**自动调用 TTS。

**AI 必做动作**：
1. 跑完 7 项 GATE 1 自检（见下文）
2. **【必做】将口播稿正文完整贴在审核申请里**（不是只贴元数据），方便用户直接审查
3. **【必做】将口播稿 .md 写入「用户当前工作目录」**（即调用方的 cwd），不是 skill 默认输出目录 `C:\Claude\wechat\`
4. 输出**自检打勾结果**（✅/❌ 列表）
5. 提交**审核申请**，明确写出：
   ```
   ⛔ GATE 1 审核申请
   - 文件路径: <用户当前工作目录>/口播稿.md
   - 字数: XXX
   - 时长预估: XX 分钟
   - 7 项自检: ✅ 6/7（第 X 项需复核）
   - 口播稿正文（已贴在上方）: ⬇
   - 等待指令: "通过" / "改 X 处" / "重写"
   ```
6. **进入等待态**，不调 TTS、不生成 MP3

**关于"输出到当前目录"的执行规则**：
- 「用户当前工作目录」= 用户发起请求时所在目录（如 `D:\wechat\排版\wiki\`），通过会话上下文判断
- 若用户显式指定输出目录，以用户指定为准
- skill 默认输出目录 `C:\Claude\wechat\` 仍可保留作为**备份**，但**首选**当前目录

**文件命名规范**（强制）：
```
<YYYYMMDD>_<内容关键词>_v<版本>.md       ← 口播稿
<YYYYMMDD>_<内容关键词>_v<版本>.mp3      ← TTS 音频
<YYYYMMDD>_<内容关键词>_v<版本>.vtt      ← WebVTT 字幕
<YYYYMMDD>_<内容关键词>_v<版本>.srt      ← SRT 字幕
<YYYYMMDD>_<内容关键词>_v<版本>.segments.json ← JSON 时间戳
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `YYYYMMDD` | 日期（生成日期，非项目日期） | `20260614` |
| `内容关键词` | 核心内容（英文或拼音，≤20字） | `skills-intro` |
| `版本` | v + 序号，首次 v1，每次修订 +1 | `v1` / `v2` |

**版本管理**：同一项目多次修订只改版本号，不改日期。旧版本保留归档。

**人类回复映射**：
- `OK / 通过 / 继续 / 可以` → 释放，进入 Phase 0.2 TTS
- `改 X 处` / `这里不对` → 修改后再次提交审核
- `重写` / `不要这版` → 回到 Phase 0.1 重新写

**AI 自检红线**（执行流水线前必读）：
- ❌ 写完口播稿直接调 TTS → 违反硬约束 1
- ✅ 任何"进入下一步"前都先停下，提交审核申请，等人类回复

---

## 流水线总览

```
Phase 0.1  写口播稿（script-writer.md）
         ↓
      ⛔ GATE 1（人工审定，必停）
         ↓
Phase 0.2  TTS 生成 MP3 + 字幕（SRT / VTT / JSON）
```

**GATE 1 是强制阻断点，未通过不能进入下游。**

---

### Phase 0.1 — 写口播稿

**触发**：本 skill `references/script-writer.md`
**关键要求**：
- 字数 **800-1200 字**（对应 4-5 分钟音频）
- "反 AI 味" 风格：口语化、有"我/你/朋友"、有具体数字、有真实场景
- 自然标点（。！？）做断句，方便后续字幕断句
- 避免 "作为 AI / 首先 / 其次 / 综上所述" 等 AI 模板语

**输出**：`口播稿.md`（含 frontmatter: voice / speed / volume / insert_pauses）

---

### ⛔ GATE 1 — 口播文案人工审定（必过）

> 🚨 **硬约束 1**：未通过此 GATE，AI **不得**进入 Phase 0.2 TTS。
> 触发 → 停下 → 提交审核申请 → 等人类回复。

> **位置**：Phase 0.1 完成后，Phase 0.2 之前
> **审核人**：人类
> **未通过**：不进入 TTS 合成

**7 项必查清单**：

| # | 检查项 | 通过标准 | 失败处理 |
|---|--------|----------|----------|
| 1 | **反 AI 味** | 口语化、有"我/你/朋友"、无模板语 | 重写 |
| 2 | **字数** | 800-1200 字（对应 4-5 分钟） | 删/补 |
| 3 | **真实数据** | 有具体数字（年份/百分比/数量） | 加数据 |
| 4 | **真实场景** | 有具体情境（时间/地点/角色） | 加场景 |
| 5 | **内容方向** | 主题与用户最初要求一致 | 重写 |
| 6 | **自然标点** | 用。！？做断句（方便字幕） | 调整 |
| 7 | **金句/收尾** | 结尾有力（评论区互动 / 升华） | 重写结尾 |

**AI 自检模板**（请求审定前必须打勾）：

```markdown
## 口播稿自检（AI 内部）
- [ ] 全文搜"作为 AI / 首先 / 其次 / 综上所述" = 0
- [ ] 全文搜"我朋友 / 你想想看 / 说白了" ≥ 2
- [ ] 具体数字（年份/百分比/数量）≥ 5 个
- [ ] 具体角色/场景 ≥ 3 个
- [ ] 字数在 800-1200 之间
- [ ] 结尾有"评论区/你怎么看"等互动
```

**通过信号**：`OK` / `通过` / `可以` / `继续`
**失败信号**：`等等，这里太 AI 味了` / `数据不够` / `结尾不够有力`

---

### Phase 0.2 — TTS 生成 MP3

**触发**：本 skill `scripts/md2mp3.py`（含停顿插入）或 `scripts/tts-gen.py`
**默认配置**：
- 音色：`moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85`（国语男声）
- 音量：1.5
- 语速：1.0
- 停顿：600ms 静音（自动在 `...` `——` `,;:` 处插入）

**输出**：`audio.mp3`

---

### Phase 0.3 — 字幕生成

**推荐方式**：`python scripts/tts-with-subs.py 口播稿.md --md --all-subs`
自动完成 TTS + SRT + VTT + JSON，**无需 Whisper**（按字数+停顿符估算，归一化到真实时长，精度 ±0.3-1s）。

**字幕断句规则**：
1. 优先标点边界（。！？）—— 避免硬切单词
2. 合并短句（< 6 字的字幕合并到下一句）
3. 拆开长句（> 18 字的字幕按次级标点拆分）
4. **最小字幕时长：不得低于 0.5s**

**输出文件**：
- `<项目名>.mp3` ← 音频
- `<项目名>.srt` ← SRT 字幕
- `<项目名>.vtt` ← WebVTT 字幕
- `<项目名>.segments.json` ← JSON 时间戳

---

---

## 📋 一键运行

```bash
# Step 1: 写口播稿（800-1200 字，反 AI 味）
# → 输出 口播稿.md
# Step 2: ⛔ GATE 1 人类审定（7 项检查）

# Step 3: 一键生成 MP3 + SRT + VTT + JSON
python scripts/tts-with-subs.py 口播稿.md --md --output <项目名> --all-subs
```

---

## 🔗 关联 Skills

| Skill | 关系 |
|-------|------|
| `mmx-tts-config` | 平行：MiniMax CLI 通用入口 |
| `multi-agent-wechat-html` | 下游：公众号长文 + 音频 |
| `multi-agent-html-media` | 平行：H5 视频页面 |

---

## 📝 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| **2.0.0** | 2026-06-14 | **精简流程**：移除 HTML 排版和 MP4 渲染，保留口播稿 → GATE1 → TTS+字幕核心流程 |
| **1.5.1** | 2026-06-14 | **Bug 修复**：SubsGen.py 短句合并 bug / base_speed 4.0 校准 / 硬切 max_chars 改标点切；tts-gen.py 流式 SSE 解析 bug / Edge TTS 兜底实现；md2mp3.py `--insert-pauses` API 调用翻倍 bug |
| **1.5.0** | 2026-06-05 | **实战模板库**：TTS 引擎降级链 / 字幕归一化算法 / 26 种版式清单 |
| **1.4.0** | 2026-06-05 | 整合 `subtitle-aligned-layout`：5 阶段流水线 / GATE 1 + GATE 2 / 防虚构 7 条戒律 |
| 1.3.0 | - | 新增 SRT/VTT/JSON 字幕轨 |
| 1.2.0 | - | 新增"脚本写手"模块（反 AI 味 10 条铁律） |
| 1.0.0 | - | 初版：TTS API + md2mp3.py / tts-gen.py |
