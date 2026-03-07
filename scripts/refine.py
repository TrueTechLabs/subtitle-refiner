#!/usr/bin/env python3
"""
Subtitle Refiner
OpenClaw Production Version
"""

import re
import os
import sys
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

class SubtitleRefinerSkill:

    FILLER_WORDS = ["嗯", "啊", "那个", "就是", "然后", "呃"]

    TERMINOLOGY_DICT = {
        "大模型": "大型语言模型",
        "rag": "RAG",
        "llm": "LLM"
    }

    # ======================
    # SRT 解析
    # ======================

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


    # ======================
    # 文本处理
    # ======================

    def refine_text(self, text):

        original = text
        cleaned = text

        # 删除句首口语词
        cleaned = re.sub(
            r'^(嗯|啊|呃|那个|就是|然后)[，。、\s]*',
            '',
            cleaned
        )

        # 删除重复空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 如果删空了恢复原文
        if not cleaned:
            cleaned = original

        return cleaned


    # ======================
    # 主处理逻辑
    # ======================

    def run(self, srt_content):

        parsed = self.parse_srt(srt_content)

        changes = []

        filler_stats = {word: 0 for word in self.FILLER_WORDS}
        term_stats = {k: 0 for k in self.TERMINOLOGY_DICT.keys()}

        for block in parsed:

            original_text = block["text"]

            cleaned = self.refine_text(original_text)

            # 统计口语词
            for word in self.FILLER_WORDS:

                count = original_text.count(word)

                if count > 0:
                    filler_stats[word] += count

            # 术语替换
            for k, v in self.TERMINOLOGY_DICT.items():

                pattern = rf'\b{k}\b'

                matches = re.findall(pattern, cleaned, flags=re.I)

                if matches:
                    term_stats[k] += len(matches)

                cleaned = re.sub(pattern, v, cleaned, flags=re.I)

            block["text"] = cleaned

            if cleaned != original_text:

                changes.append({
                    "index": block["index"],
                    "time": block["time"],
                    "original": original_text,
                    "refined": cleaned
                })

        new_srt = self.rebuild_srt(parsed)

        summary = self.generate_summary(parsed, changes, filler_stats, term_stats)

        return new_srt, summary


    # ======================
    # 生成概要
    # ======================

    def generate_summary(self, all_blocks, changes, filler_stats, term_stats):

        total_blocks = len(all_blocks)

        changed_blocks = len(changes)

        total_fillers = sum(filler_stats.values())

        total_terms = sum(term_stats.values())

        summary = f"""
📊 字幕优化概要
{'='*30}

总字幕条数：{total_blocks}
优化条数：{changed_blocks}

删除口语词：{total_fillers}
术语修正：{total_terms}

修改示例：
"""

        for change in changes[:3]:

            summary += f"""

[{change['index']}] {change['time']}
原文：{change['original']}
优化：{change['refined']}
"""

        if len(changes) > 3:
            summary += f"\n... 还有 {len(changes)-3} 处修改"

        return summary


    # ======================
    # 发送飞书
    # ======================

    def send_file(self, file_path, filename, chat_id):

        cmd = [
            "openclaw",
            "message",
            "send",
            "--channel", "feishu",
            "--target", chat_id,
            "--message", f"📄 优化后的字幕文件 {filename}",
            "--media", file_path
        ]

        subprocess.run(cmd, check=True)


    def send_summary(self, summary, chat_id):

        cmd = [
            "openclaw",
            "message",
            "send",
            "--channel", "feishu",
            "--target", chat_id,
            "--message", summary
        ]

        subprocess.run(cmd, check=True)


# ======================
# CLI
# ======================

def main():

    if len(sys.argv) < 2:

        print("Usage: refine.py <srt_file> --chat-id <chat_id>", file=sys.stderr)
        sys.exit(1)

    skill = SubtitleRefinerSkill()

    srt_file = sys.argv[1]

    chat_id = None

    if "--chat-id" in sys.argv:

        idx = sys.argv.index("--chat-id")

        if idx + 1 < len(sys.argv):
            chat_id = sys.argv[idx + 1]

    with open(srt_file, "r", encoding="utf-8-sig") as f:
        srt_content = f.read()

    new_srt, summary = skill.run(srt_content)

    base = os.path.basename(srt_file).replace(".srt", "")

    timestamp = datetime.now().strftime("%Y%m%d%H%M")

    output_filename = f"{base}_优化{timestamp}.srt"

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    out_dir = os.path.join(skill_dir, "subtitle_refine")

    os.makedirs(out_dir, exist_ok=True)

    output_path = os.path.join(out_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_srt)

    print(f"Optimized subtitle saved: {output_path}", file=sys.stderr)

    if chat_id:

        skill.send_file(output_path, output_filename, chat_id)

        skill.send_summary(summary, chat_id)

    else:

        print(new_srt)


if __name__ == "__main__":
    main()