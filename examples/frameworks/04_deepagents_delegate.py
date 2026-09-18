# /// script
# requires-python = ">=3.11"
# dependencies = ["deepagents", "langchain-openai"]
# ///
"""Deep Agents：主 Agent 委派资料员 → 读取合成资料 → 写入虚拟报告。
看点：原生 task 子 Agent 和文件工具；主 Agent 不直接持有资料查询工具。
使用默认状态内文件系统，不挂载真实目录，不提供 Shell 后端。
"""
from _common import DemoError, env, launch


async def run(_):
    from deepagents import create_deep_agent
    from langchain_openai import ChatOpenAI

    observations = []

    def read_notes(topic: str) -> str:
        """读取预置教学资料，不联网搜索，不包含外部产品事实。"""
        observations.append(topic)
        print("[资料员工具]", topic)
        return "项目甲：两步固定流程；项目乙：十步流程，第三步需要人工确认。"

    model = ChatOpenAI(model=env("OPENAI_MODEL"), timeout=40, max_retries=0)
    agent = create_deep_agent(
        model=model,
        system_prompt=("必须使用 task 委派给 notes-reader 获取资料，"
                       "随后使用 write_file 将两行摘要写入 /summary.md；不使用其他子 Agent。"),
        subagents=[{
            "name": "notes-reader", "description": "读取并总结项目资料",
            "system_prompt": "必须先调用 read_notes，再只返回两行事实，不外推。",
            "tools": [read_notes], "model": model,
        }],
    )
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "比较项目甲与乙的步骤和审批要求，生成摘要。"}]},
        {"recursion_limit": 20},
    )
    calls = [c["name"] for m in result["messages"] for c in getattr(m, "tool_calls", [])]
    print("[主 Agent 调用]", calls)
    print("[虚拟文件]", list(result.get("files", {})))
    print("[最终回复]", result["messages"][-1].content)
    if not observations or "task" not in calls or "/summary.md" not in result.get("files", {}):
        raise DemoError("本次模型没有完整完成委派、查询和虚拟文件写入，请检查上方真实轨迹。")


if __name__ == "__main__":
    launch(run, __doc__, ("OPENAI_API_KEY", "OPENAI_MODEL"))
