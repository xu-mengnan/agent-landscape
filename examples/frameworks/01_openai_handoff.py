# /// script
# requires-python = ">=3.11"
# dependencies = ["openai-agents", "openai"]
# ///
"""OpenAI Agents SDK：接待 Agent → 转交订单专家 → 只读工具查询。
看点：handoff 会改变最终回答的 Agent；不是把所有逻辑写在一个提示词里。
只使用合成订单，不修改订单，也不发送消息。
"""
from _common import DemoError, env, launch


async def run(_):
    from openai import AsyncOpenAI
    from agents import (Agent, Runner, function_tool, handoff,
                        set_default_openai_client, set_tracing_disabled)

    set_default_openai_client(AsyncOpenAI(timeout=40, max_retries=0))
    set_tracing_disabled(True)  # 教学示例不上传独立的调试 Trace。
    seen = []

    @function_tool
    def get_order(order_id: str) -> str:
        """查询合成订单；只认识 A100，不包含真实用户数据。"""
        seen.append("tool")
        print(f"[专家工具] 查询 {order_id}")
        return "A100：已发货，预计明天送达。" if order_id == "A100" else "订单不存在。"

    def transferred(_context):
        seen.append("handoff")
        print("[转交] 接待 → 订单专家")

    expert = Agent(name="订单专家", model=env("OPENAI_MODEL"), tools=[get_order],
                   instructions="先调用 get_order 核实订单，再用一句中文回答；禁止猜测状态。")
    reception = Agent(name="接待", model=env("OPENAI_MODEL"),
                      instructions="订单问题必须转交订单专家，不要自行回答。",
                      handoffs=[handoff(expert, on_handoff=transferred, tool_name_override="transfer_to_order_expert")])
    result = await Runner.run(reception, "我的 A100 订单到哪儿了？", max_turns=5)
    print("[最终回答者]", result.last_agent.name)
    print("[答案]", result.final_output)
    if seen != ["handoff", "tool"]:
        raise DemoError(f"本次未呈现预期的一次转交及一次查询，实际步骤：{seen}")


if __name__ == "__main__":
    launch(run, __doc__, ("OPENAI_API_KEY", "OPENAI_MODEL"))
