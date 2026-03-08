#!/usr/bin/env python3
"""
测试序号重复bug的修复
"""

import sys
sys.path.insert(0, 'scripts')

from refine import parse_srt, rebuild_srt, SubtitleRefiner

# 模拟测试数据 - 正常的SRT格式
test_srt = """17
00:00:39,050 --> 00:00:39,900
然后在这呢

18
00:00:39,900 --> 00:00:41,850
我们购买的话啊

19
00:00:41,850 --> 00:00:43,216
我们登录的是美区账号

20
00:00:43,216 --> 00:00:46,333
它是会提示使用那个信用卡

21
00:00:46,966 --> 00:00:49,450
那我们一般呢是没有这个信用卡的

22
00:00:54,833 --> 00:00:56,133
然后我们直接付款呢

23
00:00:56,133 --> 00:00:57,650
它是付不了的

24
00:01:00,333 --> 00:01:02,966
就是说它是会提示这个嗯"""

print("=" * 60)
print("测试SRT解析和重建")
print("=" * 60)

# 测试parse_srt
print("\n1. 测试 parse_srt:")
parsed = parse_srt(test_srt)
print(f"   解析出 {len(parsed)} 条字幕")

# 检查前几条是否正确
for i in range(min(3, len(parsed))):
    block = parsed[i]
    print(f"   [{block['index']}] text是否包含序号: {block['index'] in block['text']}")
    # 验证text中不应该包含序号
    assert block['index'] not in block['text'], f"BUG: text中包含了序号 '{block['index']}'"

# 测试rebuild_srt
print("\n2. 测试 rebuild_srt:")
rebuilt = rebuild_srt(parsed)
lines = rebuilt.split('\n')

# 检查是否有重复的序号（序号出现在text中）
print("   检查是否存在序号重复...")
has_bug = False
for i, line in enumerate(lines):
    # 检查是否是文本行（非空、非时间戳、非纯数字）
    if line and '-->' not in line and not line.isdigit():
        # 检查文本行是否以序号开头（如 "21 那我们一般..."）
        # 如果前一行是纯数字（序号），那么这一行不应该再次以该数字开头
        if i > 0 and lines[i-1].isdigit():
            index = lines[i-1]
            if line.startswith(f"{index} "):
                print(f"   ❌ 发现序号重复: [{index}] {line[:50]}")
                has_bug = True

if not has_bug:
    print("   ✅ 未发现序号重复问题")

# 打印重建后的部分内容
print("\n3. 重建后的部分内容:")
print(rebuilt[:500])
print("...")

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)
