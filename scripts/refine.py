#!/usr/bin/env python3
"""
Subtitle Refiner - 字幕去口语化与术语标准化
"""

import re
import subprocess
import tempfile
import os
import sys
import json
from datetime import datetime

class SubtitleRefinerSkill:

    name = "subtitle_refiner"
    description = "字幕去口语化与术语标准化，保持时间戳不变"

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
                    "text": " ".join(lines[2:])
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
    # 文本优化
    # ======================

    def refine_text(self, text):
        """删除口语词和多余表达"""
        cleaned = text
        for word in self.FILLER_WORDS:
            # 匹配：口气词 + 可选的逗号/句号 + 可选的空格
            pattern = word + r'[，。、\s]*'
            cleaned = re.sub(pattern, '', cleaned)

        # 去除句首标点
        cleaned = re.sub(r'^[，。、\s]+', '', cleaned)

        # 去除多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned


    # ======================
    # 发送文件到飞书
    # ======================

    def send_optimized_file(self, srt_content: str, original_filename: str, chat_id: str, skill_dir: str, source_path: str = None):
        """
        发送优化后的文件

        参数：
            srt_content: 优化后的 SRT 内容
            original_filename: 原始文件名
            chat_id: 飞书聊天 ID
            skill_dir: Skill 目录路径
            source_path: 源文件路径（可选）
        """
        # 确保 subtitle 和 subtitle_refine 文件夹存在
        subtitle_dir = os.path.join(skill_dir, 'subtitle')
        subtitle_refine_dir = os.path.join(skill_dir, 'subtitle_refine')
        os.makedirs(subtitle_dir, exist_ok=True)
        os.makedirs(subtitle_refine_dir, exist_ok=True)

        # 去掉文件名中的 UUID 后缀：---<UUID格式>
        clean_filename = re.sub(r'---[a-f0-9-]+$', '', original_filename)

        # 获取当前时间戳
        timestamp = datetime.now().strftime('%Y%m%d%H%M')

        # 生成输出文件名：源文件名_优化+时间戳
        name_part = clean_filename.replace('.srt', '').replace('.SRT', '')
        output_filename = f"{name_part}_优化{timestamp}.srt"

        # 保存源文件到 subtitle 目录（如果提供了源路径）
        if source_path and os.path.exists(source_path):
            source_dest = os.path.join(subtitle_dir, clean_filename)
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            with open(source_dest, 'w', encoding='utf-8') as f:
                f.write(source_content)

        # 保存优化后的文件到 subtitle_refine 目录
        refined_path = os.path.join(subtitle_refine_dir, output_filename)
        with open(refined_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        # 发送文件
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', chat_id,
            '--message', f'📄 优化后的字幕文件 {output_filename}\n\n请查收！',
            '--media', refined_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        return output_filename

    def send_summary(self, summary: str, chat_id: str, filename: str):
        """发送优化概要"""
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', chat_id,
            '--message', f'{summary}\n\n✅ 优化完成！文件名：{filename}'
        ]
        subprocess.run(cmd, capture_output=True, text=True)

    # ======================
    # 主处理逻辑
    # ======================

    def run(self, srt_content: str, return_summary: bool = True):

        parsed = self.parse_srt(srt_content)

        changes = []
        filler_stats = {word: 0 for word in self.FILLER_WORDS}
        term_stats = {k: 0 for k in self.TERMINOLOGY_DICT.keys()}

        for block in parsed:
            original_text = block["text"]
            cleaned = self.refine_text(block["text"])

            # 统计删除的口语词
            for word in self.FILLER_WORDS:
                count = original_text.count(word)
                if count > 0:
                    filler_stats[word] += count

            # 术语字典替换
            for k, v in self.TERMINOLOGY_DICT.items():
                count = cleaned.count(k)
                if count > 0:
                    term_stats[k] += count
                cleaned = cleaned.replace(k, v)

            block["text"] = cleaned

            # 记录变化
            if original_text != cleaned:
                changes.append({
                    "index": block["index"],
                    "time": block["time"],
                    "original": original_text,
                    "refined": cleaned
                })

        new_srt = self.rebuild_srt(parsed)

        # 生成优化概要
        if return_summary:
            summary = self.generate_summary(parsed, changes, filler_stats, term_stats)
            return new_srt, summary

        return new_srt

    def generate_summary(self, all_blocks, changes, filler_stats, term_stats):
        """生成优化概要"""
        total_blocks = len(all_blocks)
        changed_blocks = len(changes)

        total_fillers = sum(filler_stats.values())
        total_terms = sum(term_stats.values())

        summary = f"""
📊 字幕优化概要
{'=' * 40}

📈 统计信息：
  • 总字幕条数：{total_blocks}
  • 优化条数：{changed_blocks}
  • 删除口语词：{total_fillers} 个
  • 术语修正：{total_terms} 处

🗑️ 删除的口语词统计：
"""
        for word, count in filler_stats.items():
            if count > 0:
                summary += f"  • {word}：{count} 个\n"

        summary += f"""
🔄 术语修正统计：
"""
        for term, count in term_stats.items():
            if count > 0:
                summary += f"  • {term} → {self.TERMINOLOGY_DICT[term]}：{count} 处\n"

        summary += f"""
📋 详细变化（前 5 条）：
{'─' * 40}
"""
        for i, change in enumerate(changes[:5]):
            summary += f"""
  [{change['index']}] {change['time']}
  原始：{change['original']}
  优化：{change['refined']}
"""

        if len(changes) > 5:
            summary += f"\n  ... 还有 {len(changes) - 5} 处变化\n"

        return summary


# ======================
# 命令行入口
# ======================

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python refine.py <srt_file> [--chat-id <chat_id>]", file=sys.stderr)
        print("       python refine.py --stdin [--chat-id <chat_id>]", file=sys.stderr)
        sys.exit(1)

    skill = SubtitleRefinerSkill()

    # 读取 SRT 内容
    source_path = None
    if sys.argv[1] == '--stdin':
        srt_content = sys.stdin.read()
        original_filename = "stdin.srt"
    else:
        srt_file = sys.argv[1]
        source_path = srt_file
        original_filename = os.path.basename(srt_file)
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()

    # 处理字幕
    new_srt, summary = skill.run(srt_content, return_summary=True)

    # 输出
    if '--json' in sys.argv:
        print(json.dumps({
            "refined_srt": new_srt,
            "summary": summary
        }, ensure_ascii=False, indent=2))
    else:
        # 输出优化后的 SRT
        print(new_srt)

    # 如果指定了 chat_id，发送到飞书
    chat_id = None
    if '--chat-id' in sys.argv:
        idx = sys.argv.index('--chat-id')
        if idx + 1 < len(sys.argv):
            chat_id = sys.argv[idx + 1]

    if chat_id:
        # 获取 skill 目录
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 发送文件
        output_filename = skill.send_optimized_file(new_srt, original_filename, chat_id, skill_dir, source_path)
        print(f"\n✅ 已发送到飞书：{output_filename}", file=sys.stderr)

        # 发送概要
        skill.send_summary(summary, chat_id, output_filename)


if __name__ == '__main__':
    main()
