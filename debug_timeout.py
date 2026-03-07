#!/usr/bin/env python3
"""调试脚本：详细追踪API调用过程"""

import sys
import os
import json

# 设置 API Key
os.environ["SILICONFLOW_API_KEY"] = "sk-mfunaeqbxcibupnreooxribmkdfldaxgzjcobfnawqeuvmrz"

sys.path.insert(0, 'scripts')
from refine import call_siliconflow_api, parse_srt

# 读取测试文件
with open('chatgpt订阅会员教程.srt', 'r', encoding='utf-8-sig') as f:
    content = f.read()

parsed = parse_srt(content)

# 构建多chunk prompt（模拟实际场景）
chunks = [parsed[0:10], parsed[10:20]]
chunk_contents = []
for chunk_idx, chunk in enumerate(chunks):
    chunk_text = f"DATA{chunk_idx}:\n"
    for block in chunk:
        chunk_text += f'{block["index"]} {block["text"]}\n'
    chunk_contents.append(chunk_text)

prompt_content = "\n".join(chunk_contents)

system_msg = "你是字幕校对助手。只允许修正语音识别错误，不允许润色。"

multi_chunk_prompt = f"""主题：ChatGPT 使用教程

分别校对以下字幕块，返回JSON。

{prompt_content}

返回格式要求：
1. 返回JSON对象（不是数组）
2. 每个DATA块对应一个数组
3. 格式示例：{{"DATA0": ["文本1", "文本2", ...], "DATA1": ["文本3", "文本4", ...]}}
4. 确保每个数组的元素数量与输入一致（每个DATA块10个文本）
5. 不要使用markdown代码块
6. 不要添加任何解释说明"""

print("=" * 60)
print("调试多chunk API调用")
print("=" * 60)
print(f"Prompt长度: {len(multi_chunk_prompt)} 字符")
print(f"System消息: {system_msg}")
print(f"模型: Pro/zai-org/GLM-4.7")
print()

# 显示请求payload
payload = {
    "model": "Pro/zai-org/GLM-4.7",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": multi_chunk_prompt}
    ],
    "temperature": 0.2
}

print("请求Payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False)[:500] + "...")
print()

print("开始调用API（超时时间：120秒）...")
print("=" * 60)

try:
    result, in_tokens, out_tokens = call_siliconflow_api(
        multi_chunk_prompt,
        "Pro/zai-org/GLM-4.7",
        0.2,
        system_message=system_msg
    )
    print(f"✓ 成功！")
    print(f"响应长度: {len(result)} 字符")
    print(f"Token: 输入{in_tokens}, 输出{out_tokens}")
    print(f"响应前300字符:")
    print(result[:300])
except Exception as e:
    print(f"✗ 失败: {e}")
    import traceback
    print("\n详细错误:")
    traceback.print_exc()

print("=" * 60)
