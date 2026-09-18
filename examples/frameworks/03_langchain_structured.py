# /// script
# requires-python = ">=3.11"
# dependencies = ["langchain>=1,<2", "langchain-openai>=1,<2", "pydantic>=2,<3"]
# ///
"""LangChain：一句报修描述 → 有字段约束的工单对象。
看点：create_agent + ToolStrategy + Pydantic，直接拿结构化结果，不手工截取 JSON。
格式校验不等于业务事实正确；本例只提取用户已提供的信息。
"""
from typing import Literal
from _common import env, launch


async def run(_):
    from pydantic import BaseModel, Field
    from langchain.agents import create_agent
    from langchain.agents.structured_output import ToolStrategy
    from langchain_openai import ChatOpenAI

    class Ticket(BaseModel):
        device: str = Field(description="故障设备")
        symptom: str = Field(description="用户描述的症状，不补充未提及的故障")
        priority: Literal["普通", "紧急"]

    model = ChatOpenAI(model=env("OPENAI_MODEL"), timeout=40, max_retries=0)
    agent = create_agent(model=model, tools=[], response_format=ToolStrategy(Ticket),
                         system_prompt="从描述中提取工单；只有明确表示阻断工作时才标紧急。")
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "会议室打印机卡纸，今天不急。"}]},
        {"recursion_limit": 8},
    )
    ticket = result["structured_response"]
    print("[Python 对象]", type(ticket).__name__)
    print("[结构化工单]", ticket.model_dump_json(indent=2))


if __name__ == "__main__":
    launch(run, __doc__, ("OPENAI_API_KEY", "OPENAI_MODEL"))
