# /// script
# requires-python = ">=3.11"
# dependencies = ["claude-agent-sdk"]
# ///
"""Claude Agent SDK：读取一个演示代码文件 → 解释 Bug，不执行和修改代码。
看点：内置 Read 工具 + PreToolUse Hook + 流式消息。
tools 限定工具集合；Hook 再把可读路径限制为唯一文件，cwd 本身不是沙箱。
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from _common import DemoError, env, launch


async def run(_):
    from claude_agent_sdk import (ClaudeSDKClient, ClaudeAgentOptions, HookMatcher,
                                 AssistantMessage, TextBlock, ResultMessage)

    with TemporaryDirectory() as directory:
        workspace = Path(directory).resolve()
        target = workspace / "add.py"
        original = "def add(a, b):\n    return a - b  # 应当相加\n"
        target.write_text(original, encoding="utf-8")
        read_calls = []

        async def read_only(data, _tool_id, _context):
            raw = data.get("tool_input", {}).get("file_path", "")
            path = (workspace / raw).resolve() if raw else None
            allowed = data.get("tool_name") == "Read" and path == target
            if allowed:
                read_calls.append(str(path))
            print("[Hook]", "允许读取演示文件" if allowed else "拒绝非演示文件/工具")
            return {"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow" if allowed else "deny",
                "permissionDecisionReason": "只能读取临时目录中的 add.py",
            }}

        options = ClaudeAgentOptions(
            model=env("ANTHROPIC_MODEL"), cwd=str(workspace), tools=["Read"],
            permission_mode="default", setting_sources=[], strict_mcp_config=True,
            mcp_servers={}, max_turns=4, max_budget_usd=0.50,
            env={"API_TIMEOUT_MS": "60000", "CLAUDE_CODE_MAX_RETRIES": "0"},
            hooks={"PreToolUse": [HookMatcher(hooks=[read_only])]},
        )
        failed = False
        async with ClaudeSDKClient(options=options) as client:
            await client.query(f"请先读取 {target}，用两句中文解释 Bug 及修正建议。不要修改文件。")
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print("[Claude]", block.text)
                if isinstance(message, ResultMessage):
                    failed = message.is_error
        if failed or not read_calls or target.read_text(encoding="utf-8") != original:
            raise DemoError("未满足只读演示验收条件，或 SDK 返回了错误。")
        print("[验收] 实际调用了 Read，源文件未改变。")


if __name__ == "__main__":
    launch(run, __doc__, ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"))
