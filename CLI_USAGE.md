# 命令行调用指南

## 快速开始

直接通过命令行调用优化脚本：

```bash
python3 scripts/refine.py <srt_file> <chat_id> <workspace>
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `srt_file` | SRT 字幕文件的完整路径 | `/workspace/subtitle/demo.srt` |
| `chat_id` | Feishu 聊天 ID | `oc_xxxxxxxxx` |
| `workspace` | OpenClaw workspace 目录 | `/workspace` |

## 使用示例

### 示例 1：基本用法

```bash
python3 scripts/refine.py \
    /workspace/subtitle/demo.srt \
    oc_1234567890abcdef \
    /workspace
```

### 示例 2：测试本地文件

```bash
# 使用项目中的测试文件
python3 scripts/refine.py \
    test_example.srt \
    test_chat_id \
    .

# 输出文件将保存在 ./subtitle_refine/ 目录
```

### 示例 3：在 OpenClaw Skill 中使用

Agent 执行命令：

```bash
python3 {baseDir}/scripts/refine.py <srt_file> <chat_id> <workspace>
```

OpenClaw 会自动替换：
- `{baseDir}` → skill 目录路径
- `<srt_file>` → 用户上传的文件路径
- `<chat_id>` → 当前聊天 ID
- `<workspace>` → OpenClaw workspace 路径

## 返回值

- **成功**：返回退出码 0
- **失败**：返回退出码 1

## 输出

### 标准输出（stderr）

```
🔍 正在检查环境...
✓ 环境检查通过
📖 正在读取 SRT 文件: test_example.srt
🔧 正在解析 SRT...
🔍 正在分析视频主题...
✓ 检测到主题: ChatGPT 使用教程
🎯 正在优化字幕...
✓ 已处理 5 条字幕
✓ 修改了 5 处
💾 正在保存优化后的文件...
✓ 已保存到: ./subtitle_refine/test_example_优化202603072030.srt
📤 正在通过 Feishu 发送...
✓ 文件已发送: ./subtitle_refine/test_example_优化202603072030.srt
✓ 消息已发送
✅ 完成！

✓ 优化成功！
  主题: ChatGPT 使用教程
  修改: 5 处
  Token: 输入 1234, 输出 567
```

### 错误输出示例

#### API Key 未设置

```
🔍 正在检查环境...
❌ API Key 检查失败：API Key 未设置
请设置：export SILICONFLOW_API_KEY=your_key
```

#### 网络连接失败

```
🔍 正在检查环境...
🔌 无法连接到 SiliconFlow，请检查网络设置和代理配置
```

#### API Key 无效

```
🔍 正在检查环境...
❌ API Key 检查失败：API Key 无效或已过期
请设置：export SILICONFLOW_API_KEY=your_key
```

## 环境变量

必需的环境变量：

```bash
export SILICONFLOW_API_KEY=your_api_key_here
```

获取 API Key：
1. 注册账号：https://cloud.siliconflow.cn/i/AEg95IPc
2. 获取 API Key：https://cloud.siliconflow.cn/me/account/ak

## 故障排除

### 问题：命令未找到

```bash
# 使用绝对路径
/path/to/python3 /path/to/scripts/refine.py <srt_file> <chat_id> <workspace>

# 或添加到 PATH
export PATH="/path/to/python3:$PATH"
```

### 问题：权限被拒绝

```bash
# 确保脚本有执行权限
chmod +x scripts/refine.py
```

### 问题：ModuleNotFoundError

```bash
# 确保在正确的目录
cd /home/real/project/subtitle_refiner
python3 scripts/refine.py <srt_file> <chat_id> <workspace>
```

## 与 OpenClaw 集成

在 SKILL.md 中，工作流部分已更新为：

```
python3 {baseDir}/scripts/refine.py <srt_file> <chat_id> <workspace>
```

Agent 只需执行这条命令，无需编写额外的 Python 代码。
