#!/usr/bin/env python3

import os
import re
import sys
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

MODEL_ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "openclaw"


class SubtitleRefiner:

    # =====================
    # SRT 解析
    # =====================

    def parse_srt(self, content):

        blocks = re.split(r'\n\s*\n', content.strip())

        parsed = []

        for block in blocks:

            lines = block.split('\n')

            if len(lines) >= 3:

                parsed.append({
                    "index": lines[0],
                    "time": lines[1],
                    "text": "\n".join(lines[2:])
                })

        return parsed


    def rebuild_srt(self, parsed):

        result = []

        for block in parsed:

            result.append(
                f"{block['index']}\n{block['time']}\n{block['text']}"
            )

        return "\n\n".join(result)


    # =====================
    # LLM调用
    # =====================

    def call_llm(self, text, topic):

        prompt = f"""
你是专业字幕校对编辑。

视频主题：
{topic}

任务：
只修正以下问题：

1 删除口气词（嗯、啊、那个、就是等）
2 修正语音识别错误
3 保持原句意思
4 不扩写
5 不改变语气
6 保持句子长度接近

只返回优化后的字幕。

字幕：
{text}
"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        resp = requests.post(MODEL_ENDPOINT, json=payload)

        data = resp.json()

        return data["choices"][0]["message"]["content"].strip()


    # =====================
    # 主题识别
    # =====================

    def detect_topic(self, texts):

        combined = "\n".join(texts[:20])

        prompt = f"""
请总结以下字幕的主题。

只返回一句话。

字幕：
{combined}
"""

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }

        resp = requests.post(MODEL_ENDPOINT, json=payload)

        return resp.json()["choices"][0]["message"]["content"].strip()


    # =====================
    # 优化字幕
    # =====================

    def refine(self, parsed):

        texts = [b["text"] for b in parsed]

        topic = self.detect_topic(texts)

        print("Detected topic:", topic)

        changes = []

        for block in parsed:

            original = block["text"]

            try:

                refined = self.call_llm(original, topic)

            except Exception as e:

                refined = original

            block["text"] = refined

            if refined != original:

                changes.append({
                    "index": block["index"],
                    "time": block["time"],
                    "original": original,
                    "refined": refined
                })

        return parsed, topic, changes


    # =====================
    # Summary
    # =====================

    def generate_summary(self, changes):

        summary = f"""
📊 字幕优化完成

修改条数：{len(changes)}

示例修改：
"""

        for c in changes[:3]:

            summary += f"""
[{c['index']}]
原：{c['original']}
新：{c['refined']}
"""

        return summary


# =====================
# Feishu发送
# =====================

def send_file(path, filename, chat_id):

    cmd = f"""
openclaw message send \
--channel feishu \
--target {chat_id} \
--message "📄 优化后的字幕文件 {filename}" \
--media {path}
"""

    os.system(cmd)


def send_summary(summary, chat_id):

    cmd = f"""
openclaw message send \
--channel feishu \
--target {chat_id} \
--message "{summary}"
"""

    os.system(cmd)


# =====================
# CLI入口
# =====================

def main():

    if len(sys.argv) < 2:
        print("Usage: refine.py <srt_file> --chat-id xxx")
        return

    srt_file = sys.argv[1]

    chat_id = None

    if "--chat-id" in sys.argv:

        idx = sys.argv.index("--chat-id")

        if idx + 1 < len(sys.argv):

            chat_id = sys.argv[idx + 1]

    with open(srt_file, "r", encoding="utf-8-sig") as f:

        content = f.read()

    refiner = SubtitleRefiner()

    parsed = refiner.parse_srt(content)

    parsed, topic, changes = refiner.refine(parsed)

    new_srt = refiner.rebuild_srt(parsed)

    base = os.path.basename(srt_file).replace(".srt", "")

    timestamp = datetime.now().strftime("%Y%m%d%H%M")

    filename = f"{base}_优化{timestamp}.srt"

    out_dir = "subtitle_refine"

    os.makedirs(out_dir, exist_ok=True)

    output_path = os.path.join(out_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:

        f.write(new_srt)

    summary = refiner.generate_summary(changes)

    if chat_id:

        send_file(output_path, filename, chat_id)

        send_summary(summary, chat_id)

    else:

        print(new_srt)


if __name__ == "__main__":
    main()