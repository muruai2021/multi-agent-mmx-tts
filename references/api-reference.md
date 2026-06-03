# MiniMax TTS API 参考

## API 端点

| 环境 | 端点 | 说明 |
|------|------|------|
| 生产环境 | `https://api.minimax.chat/v1/t2a_v2` | 正式 API |

## 请求规范

### HTTP 方法
`POST`

### 请求头

| 头部 | 值 | 必填 |
|------|-----|------|
| Authorization | `Bearer {API_KEY}` | 是 |
| Content-Type | `application/json; charset=utf-8` | 是 |

### 请求体

```json
{
  "model": "speech-02-hd",
  "text": "要转换的文本内容",
  "stream": false,
  "voice_setting": {
    "voice_id": "moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85",
    "speed": 1.0,
    "volume": 1.5,
    "pitch": 0
  },
  "audio_setting": {
    "format": "mp3",
    "bitrate": 128000
  }
}
```

## 参数详解

### model

| 值 | 说明 |
|----|------|
| `speech-02-hd` | 高清音质（推荐）✅ |

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
| bitrate | int | 128000 | 比特率：32000-256000 |

## 响应格式

### 成功响应

```json
{
  "data": {
    "audio": "4944330400000000086a54...",  // hex 编码的音频数据
    "status": 1,
    "ced": "..."
  },
  "extra_info": {},
  "trace_id": "...",
  "base_resp": null
}
```

**重要：** 响应中的 `audio` 字段是 **hex 字符串**，不是 base64！需要用 `Buffer.from(audio, 'hex')` 解码。

### 错误响应

| 状态码 | 说明 |
|--------|------|
| 1001 | 参数错误 |
| 1002 | 内部错误 |
| 2054 | voice_id 不存在 |
| 30019 | 无权限访问该音色 |

```json
{
  "base_resp": {
    "status_code": 2054,
    "status_msg": "voice id not exist"
  }
}
```

## 调用限制

| 限制类型 | 值 |
|----------|-----|
| 单次请求文本长度 | ≤5000 字符 |
| QPS 限制 | 详见您的套餐 |
| 日调用量限制 | 详见您的套餐（免费额度有限） |

## 完整调用示例

### Node.js

```javascript
const https = require('https');
const fs = require('fs');

const apiKey = process.env.MINIMAX_API_KEY;
const text = '要转换的文本内容';

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
    format: 'mp3'
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
      // 注意：用 hex 解码，不是 base64
      const buffer = Buffer.from(result.data.audio, 'hex');
      fs.writeFileSync('C:/Claude/wechat/output.mp3', buffer);
      console.log('✅ 已保存，大小:', buffer.length, 'bytes');
    } else {
      console.error('❌ 错误:', result.base_resp);
    }
  });
});

req.on('error', console.error);
req.write(postData);
req.end();
```

### Python

```python
import requests
import os

API_KEY = os.environ.get('MINIMAX_API_KEY')
TEXT = '要转换的文本内容'

url = 'https://api.minimax.chat/v1/t2a_v2'
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}
data = {
    'model': 'speech-02-hd',
    'text': TEXT,
    'stream': False,
    'voice_setting': {
        'voice_id': 'moss_audio_ce44fc67-7ce3-11f0-8de5-96e35d26fb85',
        'speed': 1.0,
        'volume': 1.5
    },
    'audio_setting': {
        'format': 'mp3'
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result.get('data'):
    audio_data = bytes.fromhex(result['data']['audio'])
    with open('C:/Claude/wechat/output.mp3', 'wb') as f:
        f.write(audio_data)
    print(f'已保存，大小: {len(audio_data)} bytes')
else:
    print(f'错误: {result.get("base_resp")}')
```
