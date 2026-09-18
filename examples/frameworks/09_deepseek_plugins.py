# /// script
# requires-python = ">=3.11"
# dependencies = ["deepseek-harness-sdk==0.1.5rc1"]
# ///
"""DeepSeek Harness：官方 Python SDK + 配置补丁，给最小 Profile 加文件工具。
看点：profile / patches / session；不是用 Python 自己模仿 Cordis。
危险边界：sdk-minimal 自带全访问 Shell；临时目录不是隔离！只在一次性容器中运行。
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from _common import DemoError, env, launch


def options(parser):
    parser.add_argument("--isolated-runtime", action="store_true",
                        help="确认已在无敏感挂载的一次性容器/虚拟机运行；此开关本身不提供隔离")


def run(args):
    if not args.isolated_runtime:
        raise DemoError("请先使用一次性隔离环境，再加 --isolated-runtime；不要在日常宿主机直接运行。")
    from deepseek_harness import DeepSeekHarness

    patch = Path(__file__).with_name("deepseek-editor.patch.yml").resolve()
    with TemporaryDirectory() as directory:
        workspace, home = Path(directory) / "workspace", Path(directory) / "home"
        workspace.mkdir()
        home.mkdir()
        target = workspace / "greeting.txt"
        target.write_text("hello\n", encoding="utf-8")
        with DeepSeekHarness(
            provider="deepseek-official", model=env("DEEPSEEK_MODEL"), max_tokens=1024,
            cwd=str(workspace), dsh_home=str(home), profile="sdk-minimal",
            patches=(str(patch),), request_timeout_seconds=90,
        ) as harness:
            result = harness.run(
                "请使用 str_replace_editor 查看 greeting.txt，然后把 hello 替换为 hello agent。"
                "仅改此文件，不使用 Shell，不访问网络或其他目录。",
                session_id="plugin-demo",
            )
        # 提示词中的不使用 Shell 不是安全防线；隔离由外部运行环境提供。
        print("[完成原因]", result.finish_reason)
        print("[回答]", result.final_response)
        content = target.read_text(encoding="utf-8")
        print("[真实文件内容]", repr(content))
        print("[根会话事件数]", len(result.events))
        if result.finish_reason != "completed" or content.strip() != "hello agent":
            raise DemoError("未完成预期文件修改。实际使用的工具以 result.events 为准。")
        print("[边界] 文件结果不单独证明模型使用了指定插件；需检查会话事件。")


if __name__ == "__main__":
    launch(run, __doc__, ("DEEPSEEK_API_KEY", "DEEPSEEK_MODEL"), configure=options)
