---
name: subtitle-refiner
description: Process SRT subtitle files. Removes filler words, normalizes terminology, preserves timestamps, and sends the optimized subtitle file back to the user via Feishu.
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

Optimize SRT subtitles by:

- removing filler words
- standardizing terminology
- preserving timestamps exactly
- returning an optimized subtitle file

---

# When to Use

Use this skill when:

- the user uploads an `.srt` file
- the user asks to optimize subtitles
- the user asks to remove filler words
- the user asks to clean subtitle text

Examples:

- 优化这个字幕
- 去掉字幕里的口语词
- 校对字幕
- clean this subtitle file

---

# Workflow

When this skill is triggered:

1. Obtain the SRT file path provided by the user
2. Run the subtitle refinement script

```
python3 {baseDir}/scripts/refine.py <srt_file_path> --chat-id <chat_id>
```

The script will:

- parse the SRT file
- remove filler words
- normalize terminology
- preserve timestamps
- generate the optimized subtitle file
- send the file to the user through Feishu

---

# Important

The Python script is responsible for:

- generating the optimized subtitle file
- sending the file via Feishu
- sending the summary message

The agent must **only run the script**.

Do not attempt to manually send the file.

---

# Rules

Strict rules:

1. Never modify timestamps
2. Never change subtitle order
3. Never remove subtitle indices
4. Only modify subtitle text
5. Always execute the Python script

---

# Output

The script will send:

1️⃣ Optimized subtitle file (.srt)

2️⃣ Optimization summary message

Example summary:

```
📊 字幕优化概要

总字幕条数：120
优化条数：32
删除口语词：25
术语修正：10
```

---

# File Storage

Original subtitles:

```
{openclaw/workspace}/subtitle/
```

Optimized subtitles:

```
{openclaw/workspace}/subtitle_refine/
```

---

# File Naming

Optimized file format:

```
<original_name>_优化YYYYMMDDHHmm.srt
```

Example:

```
demo.srt
→
demo_优化202603072015.srt
```