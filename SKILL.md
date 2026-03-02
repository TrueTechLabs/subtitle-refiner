---
name: subtitle-refiner
description: 字幕去口语化与术语标准化，保持时间戳不变。上传 SRT 字幕文件，自动删除口气词、纠正术语并返回优化后的文件及优化概要。
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

专业字幕校对技能，用于优化视频字幕质量。

## 功能

- 删除口气词：嗯、啊、那个、就是、然后、呃
- 保持原意不变，不扩写
- 技术术语标准化
- 保持 SRT 时间戳格式不变
- 自动返回优化后的文件
- 生成优化概要报告

## 文件存储

优化后的文件保存在 skill 目录下：

- **原始字幕：** `{baseDir}/subtitle/` - 上传的原始 SRT 文件
- **优化字幕：** `{baseDir}/subtitle_refine/` - 优化后的 SRT 文件

## 文件命名格式

- **原始文件：** 保持原名（自动去除 UUID 后缀）
- **优化文件：** `源文件名_优化+时间戳.srt`
  - 示例：`chatgpt订阅会员字幕3.srt` → `chatgpt订阅会员字幕3_优化202603022159.srt`
  - 时间戳格式：`YYYYMMDDHHmm`

## 使用方法

### 方式 1：直接上传 SRT 文件
将 `.srt` 字幕文件直接发送给我，会自动优化并返回结果。

### 方式 2：使用斜杠命令
```
/subtitle-refiner <srt文件路径>
```

### 命令行使用
```bash
python3 {baseDir}/scripts/refine.py <srt文件路径> [--chat-id <chat_id>]
```

## 术语映射

- 大模型 → 大型语言模型
- rag → RAG
- llm → LLM

## 输出内容

- 优化后的 SRT 文件（通过飞书发送）
- 优化统计：
  - 总共优化多少条
  - 删除的口语词类型
  - **详细变化（前5条）**：显示前5处修改的对比

## 实现说明

使用 Python 脚本处理 SRT 文件：
- 解析 SRT 格式
- 删除口语词和多余表达
- 应用术语字典替换
- 重新构建 SRT 文件
- 原始文件保存到 `subtitle/` 目录
- 优化文件保存到 `subtitle_refine/` 目录
- 通过 OpenClaw 发送优化后的文件和概要
