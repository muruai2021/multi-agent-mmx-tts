# Multi-Agent-MMX-TTS

> MiniMax TTS 语音合成 + 反 AI 味口播脚本写手 + MD→MP3 一键转换

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()

一个面向口播创作者的 MiniMax TTS 一站式工具。除了基础的语音合成能力，还提供**反 AI 味口播脚本写手指南**和**MD→MP3 一键转换**工具，专治"AI 写稿一听就像 AI"。

---

## ✨ 核心特性

### 🎙️ 1. 完整 TTS 能力

- 6+ 种音色（国语/粤语/男女声/抒情/空乘）
- 自定义语速、音量、音调、比特率
- 支持 mp3 / wav / pcm 三种格式
- 单条、批量、流式三种调用模式

### ✍️ 2. 反 AI 味脚本写手（v1.2 核心新增）

**市面上的 TTS 工具只能"念稿"，但写出口播稿这件事更难。**

本 Skill 提供专业的"反 AI 味"口播脚本写作指南：

- ❌ **10 条反 AI 味铁律**（禁用词清单、禁用结构、禁用修辞）
- 🎣 **10 种钩子模板**（颠覆认知、痛点直击、反差冲击、悬念等）
- 🎙️ **人味细节注入**（语气词、停顿符号、自我打断、半截话）
- 📏 **节奏与时长控制**（字数/时长换算、信息密度建议）
- ✍️ **案例对照**（AI 味原稿 vs 人味改写版）
- 📋 **写前自检清单**（10 项必过）
- 🎯 **四种文体配方**（科普、故事、干货、情感）

### 🔄 3. MD→MP3 一键转换

读 Markdown 口播稿，一键生成 MP3：

- 自动解析 Frontmatter 配置（voice/speed/volume/insert_pauses）
- 自动清理 Markdown 标记
- 识别停顿符号（`...` `——`）自动插入静音
- 长文本自动分段（4500 字符/段）
- 多段音频自动合并

### 🔗 4. 与 wechat MP3 项目集成

默认输出到 `C:\Claude\wechat\`，与现有公众号口播项目天然兼容。

---

## 📁 目录结构

```
multi-agent-mmx-tts/
├── README.md                   ← 本文件
├── SKILL.md                    ← Skill 主入口（触发词、API Key 流程）
├── references/
│   ├── voice-list.md           ← 完整音色列表
│   ├── api-reference.md        ← API 参考文档（参数、错误码、限制）
│   └── script-writer.md        ← 口播脚本写手指南（反 AI 味）
└── scripts/
    ├── md2mp3.py               ← MD → MP3 一键转换
    └── tts-gen.py              ← 通用 TTS 生成器
```

---

## 🚀 快速开始

### 步骤 1：申请 API Key

1. 访问 [MiniMax 国内版](https://platform.minimaxi.com)
2. 注册/登录（手机号 / 微信 / 账号密码）
3. 进入控制台 → 「API 管理」→ 创建 API Key

> ⚠️ 国内版地址：`minimaxi.com`，**不是**国际版 `minimax.io`

### 步骤 2：设置环境变量

**Windows (PowerShell):**
```powershell
$env:MINIMAX_API_KEY="your_api_key_here"
```

**Windows (CMD):**
```cmd
set MINIMAX_API_KEY=your_api_key_here
```

**macOS / Linux:**
```bash
export MINIMAX_API_KEY="your_api_key_here"
```

### 步骤 3：安装依赖

```bash
pip install requests
```

可选（用于音频合并和停顿插入）：
```bash
# Windows: 下载 ffmpeg 并加入 PATH
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### 步骤 4：使用工具

#### 方式 A：MD → MP3 一键转换

```bash
# 最简用法（用默认国语男声）
python scripts/md2mp3.py /path/to/口播文案.md

# 启用停顿插入
python scripts/md2mp3.py 口播文案.md --insert-pauses

# 指定音色和输出
python scripts/md2mp3.py 口播文案.md --voice 国语女声 --output ./out/
```

**支持的 Frontmatter：**

```markdown
---
voice: 国语男声
speed: 1.0
volume: 1.5
insert_pauses: true
pause_ms: 600
---

# 这是标题（不读出）

正文会读出。可以 ... 表示停顿，用 —— 表示强调停顿。
```

#### 方式 B：通用 TTS 生成器

```bash
# 单条
python scripts/tts-gen.py "你好世界" --output hello.mp3

# 批量（从文件，每行一条）
python scripts/tts-gen.py --batch texts.txt --output-dir ./out/

# 流式响应
python scripts/tts-gen.py "实时语音播报" --stream

# 指定音色和语速
python scripts/tts-gen.py "测试" --voice 国语女声 --speed 1.2
```

---

## 🎤 可用音色

### 国语 / 普通话

| 音色名称 | Voice ID | 风格 |
|----------|----------|------|
| **国语男声** ⭐默认 | `moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85` | 清晰专业 |
| 国语女声 | `moss_audio_aaa1346a-7ce7-11f0-8e61-2e6e3c7ee85d` | 清晰自然 |
| 抒情男声 | `Chinese (Mandarin)_Lyrical_Voice` | 抒情悠扬 |
| 空乘女声 | `Chinese (Mandarin)_HK_Flight_Attendant` | 专业沉稳 |

### 粤语

| 音色名称 | Voice ID | 风格 |
|----------|----------|------|
| 粤语女声 | `Cantonese_GentleLady` | 温和亲切 |
| 粤语播客 | `Cantonese_podacast_host_1` | 播客风格 |

> 完整音色列表请查看 [官方文档](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)

### 场景推荐

| 场景 | 推荐音色 |
|------|----------|
| 口播配音 | 国语男声（默认） |
| 有声书 | 抒情男声 |
| 新闻播报 | 空乘女声 |
| 粤语内容 | 粤语女声 |

---

## ✍️ 反 AI 味脚本写手（核心）

**核心理念：AI 味 = 听起来像在读稿；人味 = 听起来像在跟你唠嗑。**

### 5 大反 AI 味铁律（节选）

#### ❌ 禁用词清单（部分）

| 禁用词 | 替代方案 |
|--------|----------|
| 赋能 | 帮上忙、有用 |
| 抓手 | 切入点、办法 |
| 闭环 | 完整流程 |
| 底层逻辑 | 根本原因 |
| 痛点 | 烦心事、卡住的地方 |
| 让我们共同... | 直接说 |

#### 🎣 10 种钩子模板

1. **颠覆认知型**：「你可能不信，但 XX 其实是错的」
2. **痛点直击型**：「我跟你说，这个事儿我快被它气死了」
3. **反差冲击型**：「花了 30 万买的教训，今天免费告诉你」
4. **悬念型**：「你知道为什么 XX 总是失败吗？」
5. **数字碾压型**：「一秒钟，损失 800 块」
6. **场景代入型**：「想象一下，你周一早上刚到工位...」
7. **故事开场型**：「我有个朋友，在大厂干了 8 年。上个月突然被裁了」
8. **反问型**：「你有没有这种感觉？明明很努力，但就是看不到结果」
9. **否定常识型**：「我直说，XX 这事儿其实没必要做」
10. **冒犯型**（慎用）：「说真的，听完这段的人 90% 还在用错误的方法」

**完整指南请查看** [`references/script-writer.md`](references/script-writer.md)

---

## 📊 API 参数

### voice_setting

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| voice_id | string | - | 音色 ID（必填） |
| speed | float | 1.0 | 语速 0.5-2.0 |
| volume | float | 1.0 | 音量 0.0-2.0 |
| pitch | int | 0 | 音调 -12~12 |

### audio_setting

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| format | string | mp3 | mp3 / wav / pcm |
| bitrate | int | 128000 | 32000-256000 |

**完整 API 参考请查看** [`references/api-reference.md`](references/api-reference.md)

---

## 🔗 完整工作流（与 wechat MP3 项目集成）

```
1. 选题（multi-agent-wechat skill）
   ↓
2. 用本 Skill 的"脚本写手"模块写口播稿
   ↓
3. 写入 C:\Claude\wechat\MP3\项目名\口播文案.md
   （带 Frontmatter 配置）
   ↓
4. 运行 md2mp3.py 一键生成同名 MP3
   ↓
5. 发布到公众号 / 视频号 / 抖音
```

---

## 🛠️ 开发与扩展

### 项目结构说明

- **SKILL.md** - Skill 主入口，定义触发词、API Key 流程
- **references/** - 详细文档（音色、API、写手指南）
- **scripts/** - 可执行工具脚本

### 添加新音色

编辑 `references/voice-list.md` 与 `scripts/md2mp3.py` / `scripts/tts-gen.py` 中的 `VOICE_PRESETS` 字典。

### 自定义停顿规则

修改 `scripts/md2mp3.py` 中的 `split_text_by_pauses()` 函数。

---

## ❓ 常见问题

### Q: API Key 申请需要付费吗？
A: MiniMax 提供免费额度（新用户有赠送），超出后按量付费。

### Q: 音频生成有长度限制吗？
A: 单次请求文本建议不超过 5000 字符。本工具会自动分段（4500 字符/段）。

### Q: 音频返回的是什么格式？
A: API 返回 **hex 编码**的二进制数据，需要用 `bytes.fromhex()` 或 `Buffer.from(audio, 'hex')` 解码。

### Q: 脚本写手指南能单独使用吗？
A: 可以！`references/script-writer.md` 是独立的写作指南，可配合任何 TTS 工具使用。

### Q: 是否支持流式响应？
A: 支持。使用 `tts-gen.py --stream`。

---

## 📜 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

特别欢迎：
- 新音色测试与反馈
- 新的钩子模板
- 反 AI 味规则补充
- 工具脚本优化

---

## 🔗 相关链接

- [MiniMax 国内版](https://platform.minimaxi.com)
- [MiniMax API 文档](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)
- [Claude Code](https://claude.ai/code)
- 项目仓库：https://github.com/muruai2021/multi-agent-mmx-tts

---

**让技能封装从手工业进化为流水线，从今天开始。** 🚀
