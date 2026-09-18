# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28,<1"]
# ///
"""Dify：Python 传入主题 → 平台执行已发布流程 → 读取最终输出。
看点：工作流在画布中编排，Python 只调用 API；不是在 Python 里重新造 Dify。
先按 PLATFORMS.md 建好 topic → LLM → summary 流程并取得应用 API Key。
"""
import json
from _common import DemoError, endpoint, env, launch, post_json


def run(_):
    # DIFY_BASE_URL 应包含服务 API 前缀，例如 https://api.dify.ai/v1。
    data = post_json(endpoint("DIFY_BASE_URL") + "/workflows/run", env("DIFY_API_KEY"), {
        "inputs": {"topic": "用三句话向同事解释什么是 Agent 工作流"},
        "response_mode": "blocking", "user": "agent-landscape-demo",
    })
    result = data.get("data", {})
    print("[工作流 ID]", data.get("workflow_run_id"))
    print("[状态]", result.get("status"))
    if result.get("status") != "succeeded":
        raise DemoError("工作流未成功完成；请在 Dify 运行日志查看原因，不要盲目重试。")
    outputs = result.get("outputs", {})
    if not outputs.get("summary"):
        raise DemoError("缺少 summary 输出，请检查画布的输出节点映射。")
    print("[画布执行结果]", json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    launch(run, __doc__, ("DIFY_BASE_URL", "DIFY_API_KEY"))
