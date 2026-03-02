---
name: subtitle-refiner
description: 字幕去口语化与术语标准化，保持时间戳不变。上传 SRT 字幕文件，自动删除口气词、纠正术语并返回优化后的文件及优化概要。
user-invocable: true
---

# Subtitle Refiner

专业字幕校对技能，用于优化视频字幕质量。

## 功能

- 删除口气词：嗯、啊、那个、就是、然后、呃
- 保持原意不变，不扩写
- 技术术语标准化
- 保持 SRT 时间戳格式不变
- 自动返回优化后的文件
- 生成优化概要报告

## 使用方法

### 方式 1：直接上传 SRT 文件
将 `.srt` 字幕文件直接发送给我，会自动优化并返回结果。

### 方式 2：使用斜杠命令
```
/subtitle-refiner <srt文件路径>
```

### 处理流程
1. **解析并优化**：删除口语词和多余表达
2. **应用术语字典替换**：标准化技术术语
3. **保持时间戳不变**
4. **发送优化后的文件**：将文件保存到 media/inbound 目录并发送
5. **发送优化概要**：包含统计信息和详细变化

### 新增方法

#### `process_and_send(srt_content, original_filename, chat_id)`
完整的一站式处理流程，自动完成所有步骤：
- 优化字幕内容
- 发送优化后的文件（附件形式）
- 发送详细的优化概要

#### `send_optimized_file(srt_content, original_filename, chat_id)`
将优化后的文件保存到 media/inbound 目录并作为附件发送。

#### `send_summary(summary, chat_id, filename)`
发送详细的优化统计和变化概要。

### 发送方式
优化后的文件会通过 OpenClaw 命令行工具直接发送：
```bash
openclaw message send \
  --channel feishu \
  --target <chat_id> \
  --message "📄 优化后的字幕文件 <文件名>" \
  --media <优化后的文件路径>
```

文件会被保存到 `/home/pi/.openclaw/media/inbound` 目录，确保飞书能正确识别为文件附件。

## 术语映射

- 大模型 → 大型语言模型
- rag → RAG
- llm → LLM

## 输出内容

- 优化后的 SRT 文件
- 优化统计：
  - 总共优化多少条
  - 删除的口语词类型
  - **详细变化（前5条）**：显示前5处修改的对比

## 文件位置

{baseDir}/skill.py
