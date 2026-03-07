#!/usr/bin/env python3
"""
测试脚本：验证错误处理功能

测试场景：
1. API Key 未设置
2. API Key 无效
3. 网络连接失败
4. API 超时
"""

import os
import sys

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from refine import (
    check_network_connection,
    check_api_key_validity,
    ERROR_SOLUTIONS
)


def test_network_check():
    """测试网络连接检测"""
    print("=" * 50)
    print("测试 1：网络连接检测")
    print("=" * 50)

    if check_network_connection():
        print("✅ 网络连接正常")
    else:
        print("❌ 网络连接失败")
        print(f"   {ERROR_SOLUTIONS['connection']['emoji']} {ERROR_SOLUTIONS['connection']['solution']}")


def test_api_key_check():
    """测试 API Key 验证"""
    print("\n" + "=" * 50)
    print("测试 2：API Key 验证")
    print("=" * 50)

    # 保存当前的 API Key
    original_key = os.environ.get("SILICONFLOW_API_KEY", "")

    # 测试场景 1：未设置 API Key
    print("\n场景 1：未设置 API Key")
    if "SILICONFLOW_API_KEY" in os.environ:
        del os.environ["SILICONFLOW_API_KEY"]

    # 重新导入模块以更新配置
    import importlib
    import refine
    importlib.reload(refine)

    from refine import check_api_key_validity
    valid, msg = check_api_key_validity()
    if not valid:
        print(f"✅ 正确检测到：{msg}")
    else:
        print(f"❌ 应该检测到 API Key 未设置")

    # 测试场景 2：无效的 API Key
    print("\n场景 2：无效的 API Key")
    os.environ["SILICONFLOW_API_KEY"] = "invalid_key_12345"

    # 重新导入模块
    importlib.reload(refine)
    from refine import check_api_key_validity
    valid, msg = check_api_key_validity()
    if not valid:
        print(f"✅ 正确检测到：{msg}")
    else:
        print(f"❌ 应该检测到 API Key 无效")

    # 恢复原始 API Key
    if original_key:
        os.environ["SILICONFLOW_API_KEY"] = original_key
    elif "SILICONFLOW_API_KEY" in os.environ:
        del os.environ["SILICONFLOW_API_KEY"]


def test_error_solutions():
    """测试错误提示字典"""
    print("\n" + "=" * 50)
    print("测试 3：错误提示字典")
    print("=" * 50)

    for code, info in ERROR_SOLUTIONS.items():
        print(f"\n{info['emoji']} {code}: {info['title']}")
        print(f"   解决方案：{info['solution']}")


def main():
    """运行所有测试"""
    print("🧪 错误处理功能测试\n")

    test_network_check()
    test_api_key_check()
    test_error_solutions()

    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)
    print("\n💡 提示：")
    print("1. 如果网络连接失败，请检查网络设置")
    print("2. 如果 API Key 验证失败，请设置：export SILICONFLOW_API_KEY=your_key")
    print("3. 完整测试需要有效的网络连接和 API Key")


if __name__ == "__main__":
    main()
