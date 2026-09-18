# /// script
# requires-python = ">=3.11"
# dependencies = ["agent-framework-core"]
# ///
"""Microsoft Agent Framework：解析数量 → 汇总 → 输出结果。
看点：有类型的 Executor 消息与 WorkflowBuilder；业务节点不必都调用模型。
本例不含 LLM，用三个确定性节点直接展示工作流消息传递。
"""
from typing import Never
from _common import DemoError, launch


async def run(_):
    from agent_framework import executor, WorkflowBuilder, WorkflowContext

    @executor(id="parse")
    async def parse(text: str, ctx: WorkflowContext[list[int]]) -> None:
        numbers = [int(value.strip()) for value in text.split(",")]
        print("[parse: str → list[int]]", numbers)
        await ctx.send_message(numbers)

    @executor(id="total")
    async def total(numbers: list[int], ctx: WorkflowContext[int]) -> None:
        value = sum(numbers)
        print("[total: list[int] → int]", value)
        await ctx.send_message(value)

    @executor(id="report")
    async def report(value: int, ctx: WorkflowContext[Never, str]) -> None:
        await ctx.yield_output(f"总件数：{value}")

    workflow = (WorkflowBuilder(start_executor=parse, output_from=[report])
                .add_edge(parse, total).add_edge(total, report).build())
    result = await workflow.run("3,5,2")
    outputs = result.get_outputs()
    print("[workflow output]", outputs)
    if outputs != ["总件数：10"]:
        raise DemoError("工作流输出与确定性期望不一致。")


if __name__ == "__main__":
    launch(run, __doc__, live=False)
