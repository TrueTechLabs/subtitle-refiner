# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered SRT subtitle refiner that removes filler words and fixes ASR errors while preserving timestamps. Designed as an OpenClaw Skill that integrates with Feishu messaging.

## Common Commands

### Testing

```bash
# Test error handling and environment setup
python3 test_error_handling.py

# Run syntax check on the main script
python3 -m py_compile scripts/refine.py
```

### Running the Refiner

```bash
# Direct invocation (for testing)
python3 scripts/refine.py <srt_file> <chat_id> <workspace>

# Example with test file
python3 scripts/refine.py test_example.srt test_chat_id .
```

### Environment Setup

```bash
# Set the required API key (SiliconFlow)
export SILICONFLOW_API_KEY=sk-xxxxx

# Verify the key is set
echo $SILICONFLOW_API_KEY
```

## Architecture

### Core Components

**[scripts/refine.py](scripts/refine.py)** - Main optimization module (~1000 lines)
- `SubtitleRefiner` class: Orchestrates the refinement process
- `parse_srt()` / `rebuild_srt()`: SRT parsing and reconstruction
- `refine_and_send()`: Main entry point for external calls
- Rate limiting with `RateLimiter` class (10 req/sec, 200 req/min)

**Processing Pipeline:**
1. **Environment Check** ([`refine.py:915-938`](scripts/refine.py#L915-L938)): Network connectivity + API key validation
2. **Topic Detection** ([`refine.py:403-435`](scripts/refine.py#L403-L435)): Analyzes first 20 subtitles to determine video context
3. **Batch Optimization** ([`refine.py:486-547`](scripts/refine.py#L486-L547)): Concurrent processing with rate limiting
   - Small files (≤30 lines): Line-by-line processing
   - Large files: Batched (5 lines/batch) with ThreadPoolExecutor (max 10 workers)
4. **Output & Send** ([`refine.py:962-1005`](scripts/refine.py#L962-L1005)): Saves to `{workspace}/subtitle_refine/` and sends via OpenClaw

### API Configuration

Located at top of [scripts/refine.py](scripts/refine.py#L26-L67):
- **Primary Model**: `Pro/zai-org/GLM-4.7`
- **Fallback Model**: `Qwen/Qwen2.5-7B-Instruct`
- **Endpoint**: `https://api.siliconflow.cn/v1/chat/completions`
- **Environment**: `SILICONFLOW_API_KEY` (required)

### Error Handling

Comprehensive error mapping in `ERROR_SOLUTIONS` dictionary ([`refine.py:35-67`](scripts/refine.py#L35-L67)):
- 401: API Key errors
- 402/403: Balance/permission issues
- 429: Rate limiting
- timeout/connection: Network issues

All errors are caught early via pre-flight checks ([`refine.py:133-179`](scripts/refine.py#L133-L179)).

## Key Constraints

### SRT Processing Rules
- **Never modify** timestamps, index numbers, or subtitle order
- **Only modify** the text content of subtitle entries
- Preserve original meaning and tone - only remove filler words and fix obvious ASR errors

### Rate Limiting
The `RateLimiter` class enforces:
- 10 requests per second
- 200 requests per minute
- Automatic waiting when limits are reached

### Prompt Engineering
Two distinct prompts used:

**Topic Detection** ([`refine.py:416-423`](scripts/refine.py#L416-L423)): Summarizes video theme from first 20 lines

**Line Refinement** ([`refine.py:452-467`](scripts/refine.py#L452-L467)): 6 rules for minimal text changes
- Remove filler words (嗯, 啊, 那个, 就是, 然后, 呃)
- Fix ASR errors (XGBT→ChatGPT, RG→RAG, etc.)
- No expansion or rewriting
- Preserve tone

## Integration Points

### OpenClaw Skill Framework
- **Trigger**: User uploads `.srt` file or uses keywords ("优化字幕", "fix subtitle")
- **Entry Point**: Command line execution of `scripts/refine.py`
- **Output**: Sends optimized file + summary message via `openclaw message send --channel feishu`

### File Paths
- **Input**: `{workspace}/subtitle/` (managed by OpenClaw)
- **Output**: `{workspace}/subtitle_refine/{filename}_优化_{timestamp}.srt`
- **Test Data**: [test_example.srt](test_example.srt) in project root

## Making Changes

When modifying the refiner:

1. **Prompt Changes**: Edit prompts in `detect_topic()` or `refine_subtitle_line()` methods
2. **Model Selection**: Change `PRIMARY_MODEL`/`FALLBACK_MODEL` constants at top of file
3. **Rate Limits**: Adjust `max_per_second`/`max_per_minute` in `API_RATE_LIMITER` initialization
4. **Batch Size**: Modify `mini_batch_size` in `refine_batch()` method

Always test with:
```bash
python3 test_error_handling.py  # Environment checks
python3 scripts/refine.py test_example.srt test_chat_id .  # Functional test
```
