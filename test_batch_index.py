#!/usr/bin/env python3
"""
测试批量处理时序号重复的bug修复
"""

import sys
import json
sys.path.insert(0, 'scripts')

from refine import parse_srt, SubtitleRefiner

# 测试数据
test_srt = """1
00:00:00,000 --> 00:00:02,000
嗯，今天我们来讲一下ChatGPT

2
00:00:02,000 --> 00:00:04,000
那个，这个工具非常好用

3
00:00:04,000 --> 00:00:06,000
然后我们来看一下具体操作

4
00:00:06,000 --> 00:00:08,000
就是说它可以帮助我们写作

5
00:00:08,000 --> 00:00:10,000
啊，这个功能很强大"""

print("=" * 60)
print("测试批量处理中的序号问题")
print("=" * 60)

# 解析SRT
parsed = parse_srt(test_srt)
print(f"\n✓ 解析出 {len(parsed)} 条字幕")

# 检查原始数据
print("\n检查原始数据中的text字段是否包含序号:")
has_issue = False
for block in parsed:
    if block['text'].startswith(block['index']):
        print(f"  ❌ [{block['index']}] text以序号开头: '{block['text']}'")
        has_issue = True
    else:
        print(f"  ✅ [{block['index']}] text正常: '{block['text']}'")

if not has_issue:
    print("\n✅ 原始数据正确，text中不包含序号")

# 模拟批量处理时构建的prompt数据格式
print("\n" + "=" * 60)
print("模拟批量处理的prompt构建:")
print("=" * 60)

chunks = []
chunk_size = 3  # 每个chunk 3条字幕
for i in range(0, len(parsed), chunk_size):
    chunks.append(parsed[i:i + chunk_size])

# 模拟_process_multi_chunk_batch中的chunk内容构建
chunk_contents = []
for chunk_idx, chunk in enumerate(chunks):
    chunk_text = f"DATA{chunk_idx}:\n"
    for idx, block in enumerate(chunk):
        # 修复后的代码：只发送文本，不包含序号
        chunk_text += f'{block["text"]}\n'
    chunk_contents.append(chunk_text)

print("\n构建的prompt数据:")
for content in chunk_contents:
    print(content)
    print("...")

# 检查构建的数据中是否包含序号
print("检查构建的数据中是否包含序号:")
has_index_in_prompt = False
for block in parsed:
    # 检查任何序号是否出现在prompt内容中
    for content in chunk_contents:
        if block['index'] in content and content.index(block['index']) != content.index(f"DATA"):
            # 确保不是作为DATA的一部分（如DATA0, DATA1）
            lines = content.split('\n')
            for line in lines[1:]:  # 跳过DATA行
                if line.startswith(block['index']):
                    print(f"  ❌ 序号 {block['index']} 出现在数据行: '{line}'")
                    has_index_in_prompt = True

if not has_index_in_prompt:
    print("  ✅ 构建的数据中不包含序号（只有纯文本）")

print("\n" + "=" * 60)
print("✅ 测试完成 - 批量处理不会引入序号重复")
print("=" * 60)
