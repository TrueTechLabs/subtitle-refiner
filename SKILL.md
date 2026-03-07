---
name: subtitle-refiner
description: Processes SRT subtitle files by removing filler words, standardizing terminology, and preserving timestamps exactly. Use when a user uploads or requests optimization of subtitles.
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

Subtitle Refiner 是一个 **SRT 字幕优化技能**。  
用于清理口语化表达、统一技术术语，并在 **完全保持时间轴不变的前提下**生成优化后的字幕文件。

该技能适用于视频字幕整理、课程字幕优化、技术视频字幕标准化等场景。

---

# When to Use

当满足以下情况时应调用该技能：

- 用户上传 `.srt` 字幕文件
- 用户请求：
  - 优化字幕
  - 校对字幕
  - 去掉口语词
  - 标准化字幕术语
- 用户需要 **保持字幕时间轴不变**

示例触发语句：

- 优化这个字幕
- 帮我清理字幕口语词
- 校对这个 SRT
- 优化视频字幕

---

# Workflow

执行流程：

1. 接收用户提供的 `.srt` 文件
2. 调用 Python 脚本解析 SRT 结构
3. 对字幕文本执行优化：
   - 删除口语词
   - 清理冗余表达
   - 执行术语标准化
4. **保持所有时间戳完全不变**
5. 重建合法 SRT 文件
6. 保存优化后的字幕
7. 生成优化统计
8. 返回优化字幕文件和摘要报告

---

# Text Processing Rules

## 删除口语词

自动删除以下口语词：

- 嗯
- 啊
- 呃
- 那个
- 就是
- 然后

示例：

原文

```
嗯 我觉得这个其实还可以
```

优化后

```
我觉得这个其实还可以
```

---

# Terminology Standardization

统一以下技术术语：

| 原词 | 替换 |
|-----|-----|
| 大模型 | 大型语言模型 |
| rag | RAG |
| llm | LLM |

---

# Critical Rules

执行时必须遵守：

1. **绝对不能修改时间戳**
2. **绝对不能删除字幕编号**
3. **绝对不能改变字幕顺序**
4. 仅允许修改字幕文本
5. 必须保持 SRT 格式合法

如果无法保证以上规则，则必须停止处理。

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

原始文件：

```
保持原始文件名
```

优化文件：

```
源文件名_优化YYYYMMDDHHmm.srt
```

示例：

```
xx视频字幕.srt
→
xx视频字幕_优化202603022159.srt
```

时间戳格式：

```
YYYYMMDDHHmm
```

---

# Usage

## 上传文件

直接发送 `.srt` 文件即可自动处理。

---

## Slash Command

```
/subtitle-refiner <srt文件路径>
```

---

## CLI 调用

```bash
python3 {baseDir}/scripts/refine.py <srt文件路径> [--chat-id <chat_id>]
```

---

# Output

执行完成后返回：

## 1 优化字幕文件

返回 `.srt` 文件。

---

## 2 优化统计

报告包含：

- 字幕总条数
- 修改条数
- 删除的口语词类型
- 优化比例

---

## 3 修改示例

显示 **前 5 条修改对比**

示例：

原文

```
嗯 我觉得这个其实还可以
```

优化后

```
我觉得这个其实还可以
```

---

# Implementation

实现脚本：

```
{baseDir}/scripts/refine.py
```

脚本流程：

1. 解析 SRT 文件结构
2. 删除口语词
3. 替换术语
4. 保持时间轴不变
5. 生成优化字幕
6. 保存文件
7. 返回优化结果