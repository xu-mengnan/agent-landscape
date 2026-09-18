# /// script
# requires-python = ">=3.11"
# dependencies = ["google-adk>=2,<3"]
# ///
"""Google ADK：写作者 → 审阅者；按顺序执行并共享 Session 状态。
看点：SequentialAgent + output_key；第二个 Agent 通过 {draft} 读取第一个的输出。
固定两步，不让模型自己猜执行顺序。
"""
import os
from _common import DemoError, env, launch


async def run(_):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"  # 本例明确使用 API Key 路线。
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.apps import App
    from google.adk.runners import InMemoryRunner

    writer = LlmAgent(
        name="writer", model=env("GOOGLE_MODEL"), output_key="draft",
        instruction="写两句中文介绍分层记忆，不编造量化效果。只输出草稿。",
    )
    reviewer = LlmAgent(
        name="reviewer", model=env("GOOGLE_MODEL"), output_key="review",
        instruction="审阅草稿：{draft}。指出一句可能被误解的话，并给出更准确的改写。",
    )
    pipeline = SequentialAgent(name="write_then_review", sub_agents=[writer, reviewer])
    runner = InMemoryRunner(app=App(name="adk_pipeline_demo", root_agent=pipeline))
    events = await runner.run_debug("请生成并审阅这份介绍。")
    authors = set()
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    authors.add(event.author)
                    print(f"[{event.author}] {part.text}")
    if not {"writer", "reviewer"}.issubset(authors):
        raise DemoError("没有观察到两个 Agent 的文本输出，不能认定顺序流程已完成。")


if __name__ == "__main__":
    launch(run, __doc__, ("GOOGLE_API_KEY", "GOOGLE_MODEL"))
