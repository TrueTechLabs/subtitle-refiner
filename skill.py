import re
import subprocess
import tempfile
import os

class SubtitleRefinerSkill:

    name = "subtitle_refiner"
    description = "字幕去口语化与术语标准化，保持时间戳不变，并发送至飞书"

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
    # 调用 OpenClaw 内置模型
    # ======================

    def refine_text(self, text):
        # 方法 1: 使用字典规则（快速、免费）
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
    # 新增：处理并发送文件
    # ======================

    def process_and_send(self, srt_content: str, original_filename: str, chat_id: str):
        """
        完整的处理流程：
        1. 处理字幕
        2. 发送优化后的文件
        3. 发送优化概要
        """
        # 步骤 1: 处理字幕
        new_srt, summary = self.run(srt_content, return_summary=True)

        # 步骤 2: 发送优化后的文件
        output_filename = self.send_optimized_file(new_srt, original_filename, chat_id)

        # 步骤 3: 发送优化概要
        self.send_summary(summary, chat_id, output_filename)

        return output_filename

    def send_optimized_file(self, srt_content: str, original_filename: str, chat_id: str):
        """
        发送优化后的文件

        使用 media/inbound 目录作为文件存储位置
        """
        import uuid

        # 生成输出文件名
        name_part = original_filename.replace('.srt', '').replace('.SRT', '')
        output_filename = f"{name_part}_优化后.srt"

        # 保存到 media/inbound 目录
        media_dir = "/home/pi/.openclaw/media/inbound"
        unique_suffix = str(uuid.uuid4())[:12]
        file_path = os.path.join(media_dir, f"{name_part}---{unique_suffix}")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        # 同时保存为标准文件名（如果已存在则覆盖）
        standard_path = os.path.join(media_dir, output_filename)
        with open(standard_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        # 发送文件
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', chat_id,
            '--message', f'📄 优化后的字幕文件 {output_filename}\n\n请查收！',
            '--media', standard_path
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
    # 主入口（保持向后兼容）
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

        # 如果需要发送到飞书，取消下面的注释
        # self.send_to_feishu(new_srt)

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

    def send_file_to_feishu(self, srt_content: str, original_filename: str, chat_id: str = None):
        """
        将优化后的字幕文件发送到飞书（保留向后兼容）

        参数：
            srt_content: 优化后的 SRT 内容
            original_filename: 原始文件名（用于生成输出文件名）
            chat_id: 飞书聊天 ID（可选，如果为 None 则返回文件路径）

        返回：
            (temp_file_path, output_filename) - 临时文件路径和输出文件名
        """
        # 生成输出文件名
        name_part = original_filename.replace('.srt', '').replace('.SRT', '')
        output_filename = f"{name_part}_优化后.srt"

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as f:
            f.write(srt_content)
            temp_file_path = f.name

        try:
            # 如果没有提供 chat_id，返回文件路径让调用者处理
            if chat_id is None:
                return temp_file_path, output_filename

            # 构建 openclaw message send 命令
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'feishu',
                '--target', chat_id,
                '--message', f'✅ 文件已发送成功！\n优化后的字幕文件 {output_filename} 已发送给你。',
                '--media', temp_file_path
            ]

            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return temp_file_path, output_filename
            else:
                # 如果命令执行失败，返回文件路径让调用者处理
                return temp_file_path, output_filename

        except Exception as e:
            # 如果出现异常，返回文件路径让调用者处理
            return temp_file_path, output_filename
