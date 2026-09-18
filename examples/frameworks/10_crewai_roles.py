# /// script
# requires-python = ">=3.11"
# dependencies = ["crewai"]
# ///
"""CrewAI：分析员提炼事实 → 编辑把分析结果写成简报。
看点：角色/目标/背景 + Task.context + 顺序 Crew；不是两个 Agent 各自聊天。
资料固定且合成，不联网研究，也不宣称内容已经过事实审计。
"""
from _common import DemoError, env, launch


def run(_):
    from crewai import Agent, Task, Crew, Process, LLM

    llm = LLM(model="openai/" + env("OPENAI_MODEL"), timeout=40)
    analyst = Agent(role="资料分析员", goal="只提炼给定资料中的事实",
                    backstory="你负责区分事实和建议，不猜测缺失信息。",
                    llm=llm, allow_delegation=False, max_iter=3)
    editor = Agent(role="简报编辑", goal="将分析员的结果压缩成可读简报",
                   backstory="你面对没有技术背景的读者，不发明指标。",
                   llm=llm, allow_delegation=False, max_iter=3)
    extract = Task(description="提炼这些合成事实：{facts}", expected_output="两条事实",
                   agent=analyst)
    brief = Task(description="根据前置任务结果，写一句结论和一条建议，明确标注建议。",
                 expected_output="两行中文简报", agent=editor, context=[extract])
    crew = Crew(agents=[analyst, editor], tasks=[extract, brief],
                process=Process.sequential, verbose=False)
    result = crew.kickoff(inputs={"facts": "系统甲只保存最近5轮对话；系统乙另有带版本的偏好记录。"})
    if extract.output is None or not result.raw:
        raise DemoError("前置任务或最终简报没有输出。")
    print("[分析员]", extract.output.raw)
    print("[编辑]", result.raw)


if __name__ == "__main__":
    launch(run, __doc__, ("OPENAI_API_KEY", "OPENAI_MODEL"))
