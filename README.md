# Subtitle Refiner 📝

> AI 驱动的 SRT 字幕优化工具 - OpenClaw Skill

使用  GLM-4.7 大语言模型智能优化字幕文件，去除口语填充词，修正语音识别错误，保持时间轴完全不变。

## ✨ 核心功能

- **🎯 智能去词**：自动删除 "嗯"、"啊"、"那个"、"就是"、"然后"、"呃" 等口语填充词
- **🔧 ASR 修正**：根据视频主题智能修正语音识别错误
  - `XGBT` → `ChatGPT`
  - `RG` → `RAG`
  - `菜GPT` → `ChatGPT`
  - `CHATPT` → `ChatGPT`
  - 更多上下文相关的错误修正...
- **⏱️ 时间轴保护**：所有时间戳信息完全不变
- **🧠 主题感知**：分析视频主题，进行上下文相关的智能校对
- **📊 Token 追踪**：详细记录每次优化的 AI 消耗
- **📤 自动发送**：通过 Feishu 自动发送优化结果

## 📋 优化效果示例

### 优化前

```srt
1
00:00:00,000 --> 00:00:02,500
嗯，这个XGBT很好用

2
00:00:02,500 --> 00:00:05,000
然后啊，就是我们可以用RG技术
```

### 优化后

```srt
1
00:00:00,000 --> 00:00:02,500
这个ChatGPT很好用

2
00:00:02,500 --> 00:00:05,000
然后，我们可以用RAG技术
```

### 优化总结

```
📊 字幕优化完成

本次消耗token：输入1234 输出567，共修改了15处，以下为前3处：

[1]
原：嗯，这个XGBT很好用
新：这个ChatGPT很好用

[2]
原：然后啊，就是我们可以用RG技术
新：然后，我们可以用RAG技术
```

## 🚀 安装

> 在小龙虾聊天窗口发送：
```bash
安装技能：https://github.com/TrueTechLabs/subtitle_refiner 
配置当前shell环境变量：SILICONFLOW_API_KEY=sk-m******
```
注册领域16代金券 https://cloud.siliconflow.cn/i/AEg95IPc

获取SILICONFLOW_API_KEY：https://cloud.siliconflow.cn/me/account/ak

手动操作
```bash
# 也可手动下载项目复制到 OpenClaw skills 目录
cp -r subtitle_refiner ~/.openclaw/skills/subtitle-refiner
# 配置环境变量到.bashrc/.zshrc
export SILICONFLOW_API_KEY=sk-m******
```


## 📖 使用方法

### 自动触发（推荐）

当以下情况时，OpenClaw 会自动触发此技能：

1. **用户上传 .srt 文件**
2. **用户发送关键词**：
   - "优化字幕"
   - "校对字幕"
   - "去掉字幕里的口语词"
   - "fix subtitle"
   - "refine subtitle"

示例对话：

```
用户：[上传 demo.srt 文件]

Agent：收到字幕文件，开始优化...
🔍 正在分析视频主题...
✓ 检测到主题: ChatGPT 使用教程
🎯 正在优化字幕...
✓ 已处理 150 条字幕
✓ 修改了 23 处
📤 正在通过 Feishu 发送...
✅ 完成！
```

## ⚙️ 配置

### API 配置

默认使用 SiliconFlow API：

| 配置项 | 值 |
|--------|-----|
| Endpoint | `https://api.siliconflow.cn/v1/chat/completions` |
| 主模型 | `Pro/zai-org/GLM-4.7` |
| 备用模型 | `Qwen/Qwen2.5-7B-Instruct` |

如需更换模型，编辑 [`scripts/refine.py`](scripts/refine.py) 中的配置：

```python
PRIMARY_MODEL = "Pro/zai-org/GLM-4.7"  # 主模型
FALLBACK_MODEL = "Qwen/Qwen2.5-7B-Instruct"  # 备用模型
```

### 文件存储

- **输入文件**：`{workspace}/subtitle/`（由 OpenClaw 管理）
- **输出文件**：`{workspace}/subtitle_refine/`
- **命名格式**：`{原文件名}_优化{时间戳}.srt`

## 🔧 工作原理

### 优化流程

1. **解析 SRT**：读取并解析字幕文件，保持索引和时间戳
2. **主题分析**：使用 LLM 分析前 20 条字幕，提取视频主题
3. **逐行优化**：基于主题和规则，逐条优化字幕文本
4. **生成总结**：统计修改数量和 token 消耗
5. **发送结果**：通过 Feishu 发送优化文件和总结

### 提示词策略

**主题分析提示词**：

```
请分析以下字幕内容的主题。
请用一句话总结这个视频的主要内容是什么。
字幕内容：[前 20 条字幕]
只返回主题描述，不要解释。
```

**逐行优化提示词**：

```
你是专业字幕校对编辑。
视频主题：{检测到的主题}

任务：只修正以下问题，不要做其他改动：
1. 删除口语语气词（嗯、啊、那个、就是、然后、呃等）
2. 修正语音识别错误（如：XGBT→ChatGPT，RG→RAG）
3. 保持原句意思完全不变
4. 不扩写、不缩写
5. 不改变语气

只返回优化后的字幕，不要解释。
原字幕：{原文}
```

### 质量保证

- **Temperature 0.2**：确保输出稳定性
- **规则约束**：6 条明确规则，避免过度修改
- **错误处理**：主模型失败时自动切换备用模型

## 🛠️ 故障排除

### 问题：API 调用失败

**错误信息**：`API 调用失败: ...`

**解决方案**：
1. 检查 API Key 是否正确设置
2. 确认网络连接正常
3. 检查 SiliconFlow 服务状态
4. 查看是否有足够的 API 额度



## 🤝 贡献

欢迎提交 Issue 和 Pull Request！


## 📄 许可证

MIT License



**Made with ❤️ by Subtitle Refiner Team**
