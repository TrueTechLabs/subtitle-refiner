---
name: subtitle-refiner
description: Optimize SRT subtitle files by removing filler words and standardizing terminology while preserving timestamps exactly. When a user uploads an SRT file, process it and send the optimized file back via Feishu.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "requires": { "bins": ["python3"] }
      }
  }
---

# Subtitle Refiner

字幕优化技能，用于：

- 删除口语词
- 标准化术语
- 保持 SRT 时间戳完全不变
- 返回优化后的字幕文件

---

# When to use

当用户：

- 上传 `.srt` 文件
- 说 “优化字幕”
- 说 “去掉口语词”
- 说 “校对字幕”

必须调用此技能。

---

# Workflow

1. 获取用户提供的 `.srt` 文件路径
2. 运行脚本处理字幕

```
python3 {baseDir}/scripts/refine.py <srt文件路径> --chat-id <chat_id>
```

脚本会：

- 解析字幕
- 删除口语词
- 标准化术语
- 生成优化字幕
- 返回文件路径

---

# IMPORTANT: Send file back to user

优化完成后 **必须发送文件**，不要只发送文本。

使用 OpenClaw CLI：

```
openclaw message send \
  --channel feishu \
  --target <chat_id> \
  --message "📄 优化后的字幕文件 <文件名>" \
  --media <优化后的文件路径>
```

必须发送文件。

禁止只返回文字。

---

# Rules

执行时必须遵守：

1. 不允许修改时间戳
2. 不允许删除字幕编号
3. 不允许改变字幕顺序
4. 仅允许修改字幕文本
5. 必须返回优化后的字幕文件

---

# Output

执行后：

1. 发送优化后的 `.srt` 文件
2. 再发送优化统计：

示例：

```
📊 字幕优化概要

总字幕条数：120
优化条数：35
删除口语词：28
术语修正：12
```

---

# File Storage

原始字幕：

```
{openclaw/workspace}/subtitle/
```

优化字幕：

```
{openclaw/workspace}/subtitle_refine/
```

---

# File Naming

输出文件：

```
源文件名_优化YYYYMMDDHHmm.srt
```

示例：

```
demo.srt
→
demo_优化202603072015.srt
```