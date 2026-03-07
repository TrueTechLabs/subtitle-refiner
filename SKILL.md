---
name: subtitle-refiner
description: 优化 SRT 字幕文件。去除填充词（嗯、啊等），修正 ASR 识别错误（如 XGBT→ChatGPT、RG→RAG），保持时间戳完全不变，通过 Feishu 发送优化结果和 token 消耗报告。
user-invocable: true
metadata:
{
  "openclaw": {
    "emoji": "📝",
    "requires": {
      "bins": ["python3"],
      "env": ["SILICONFLOW_API_KEY"]
    },
    "primaryEnv": "SILICONFLOW_API_KEY"
  }
}
---

# Subtitle Refiner

AI 驱动的字幕优化工具，使用 SiliconFlow GLM-4.7 模型智能优化 SRT 字幕文件。

## 核心功能

- **自动去除语气词**：删除 "嗯"、"啊"、"那个"、"就是"、"然后"、"呃" 等口语填充词
- **智能修正 ASR 错误**：根据视频主题修正语音识别错误
  - XGBT → ChatGPT
  - RG → RAG
  - 菜GPT → ChatGPT
  - CHATPT → ChatGPT
  - 等等...
- **保持时间戳**：所有时间轴信息完全不变
- **主题感知**：分析视频主题，进行上下文相关的校对
- **Token 追踪**：详细记录每次优化的 token 消耗

---

## 触发条件

当以下情况时自动触发此技能：

1. **用户发送 .srt 文件**
2. **用户使用关键词**：
   - "优化字幕"
   - "校对字幕"
   - "去掉字幕里的口语词"
   - "fix subtitle"
   - "refine subtitle"
   - "clean subtitle"

---

## 工作流程

当技能被触发时：

### 步骤 1：获取文件路径

从用户消息中获取 SRT 文件路径。

### 步骤 2：调用优化模块

使用以下 Python 代码调用优化模块：

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")
from refine import refine_and_send

# 调用优化函数
refine_and_send(
    srt_file_path="<SRT 文件路径>",
    chat_id="<Feishu chat ID>",
    workspace_dir="<OpenClaw workspace 目录>"
)
```

**参数说明**：
- `srt_file_path`: SRT 文件的完整路径
- `chat_id`: Feishu 聊天 ID（从上下文获取）
- `workspace_dir`: OpenClaw workspace 目录（用于存储输出文件）

### 步骤 3：发送结果

脚本会自动：
1. 生成优化后的字幕文件
2. 通过 Feishu 发送文件
3. 发送优化总结（包含 token 消耗和修改明细）

---

## 重要规则

Agent **必须**遵守以下规则：

1. ✅ **保持时间戳**：永远不修改时间轴信息
2. ✅ **保持顺序**：永远不改变字幕顺序
3. ✅ **保持索引**：永远不修改字幕序号
4. ✅ **只修改文本**：只修改字幕的文本内容
5. ✅ **调用 Python 模块**：使用上述代码导入并调用 `refine_and_send()`
6. ✅ **传递正确参数**：确保传递文件路径、chat_id 和 workspace_dir

---

## 输出格式

### 优化后的文件

- **命名格式**：`{原文件名}_优化{时间戳}.srt`
- **存储位置**：`{workspace}/subtitle_refine/`
- **发送方式**：通过 `openclaw message send --channel feishu --target {chat_id} --media {path}`

### 优化总结

发送到 Feishu 的消息格式：

```
📊 字幕优化完成

本次消耗token：输入1234 输出567，共修改了15处，以下为前3处：

[2]
原：怎么升级XGBT会员
新：怎么升级ChatGPT会员

[9]
原：下载一下这QQ的JPT
新：下载一下ChatGPT

[13]
原：这有一个升级至签GPT plus
新：这有一个升级至ChatGPT Plus
```

---

## 配置

### API 配置

- **Endpoint**: `https://api.siliconflow.cn/v1/chat/completions`
- **主模型**: `Pro/zai-org/GLM-4.7`
- **备用模型**: `Qwen/Qwen2.5-7B-Instruct`
- **API Key**: 从环境变量 `SILICONFLOW_API_KEY` 读取

### 文件存储

- **原始文件**: `{workspace}/subtitle/`（由 OpenClaw 管理）
- **优化文件**: `{workspace}/subtitle_refine/`（输出目录）

---

## 错误处理

如果遇到以下错误：

1. **API Key 缺失**
   - 提示用户设置环境变量：`export SILICONFLOW_API_KEY=your_key`

2. **API 调用失败**
   - 脚本会自动尝试备用模型
   - 如果都失败，返回原始文件

3. **文件格式错误**
   - 检查是否为有效的 SRT 格式
   - 确保文件编码为 UTF-8

---

## 示例对话

**用户**：上传 `demo.srt` 文件

**Agent**：
```
收到字幕文件，开始优化...

[调用 refine_and_send() 模块]

✅ 优化完成！已发送到 Feishu。
```

---

## 技术细节

### 提示词策略

1. **主题分析**：分析前 20 条字幕，提取视频主题
2. **逐行优化**：基于主题和规则，逐行校对每条字幕
3. **规则约束**：6 条明确规则，确保不过度修改

### Token 追踪

- 每次API调用都记录输入和输出 token
- 汇总所有调用的总消耗
- 在总结中清晰展示

### 优化质量

- Temperature: 0.2（确保稳定性）
- 仅修正明确的问题，不润色
- 保持原句意思和语气
