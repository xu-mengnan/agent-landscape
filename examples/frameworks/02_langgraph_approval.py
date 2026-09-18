# /// script
# requires-python = ">=3.11"
# dependencies = ["langgraph>=1,<2", "langgraph-checkpoint-sqlite"]
# ///
"""LangGraph：生成草稿 → 暂停等审批 → 从 SQLite 继续执行。
看点：interrupt / Command / checkpointer；完全不需要模型或 API Key。
关闭数据库连接并重新构图后继续，演示持久化读取，不冒充进程崩溃测试。
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypedDict
from _common import DemoError, launch


class State(TypedDict):
    draft: str
    approved: bool
    result: str


def options(parser):
    parser.add_argument("--decision", choices=["approve", "reject"], default="reject",
                        help="模拟审批输入；默认拒绝，不发送任何真实消息")


def run(args):
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import Command, interrupt
    from langgraph.checkpoint.sqlite import SqliteSaver

    def prepare(state):
        return {"draft": "你好，这是待审核的演示通知。"}

    def approve(state):
        # 恢复时节点会重跑，因此 interrupt 前不放不可重复的业务动作。
        answer = interrupt({"question": "是否批准这份草稿？", "draft": state["draft"]})
        return {"approved": answer is True}

    def finish(state):
        return {"result": "批准：仅展示草稿，不发送" if state["approved"] else "拒绝：停止"}

    def build(checkpointer):
        graph = StateGraph(State)
        for name, node in [("prepare", prepare), ("approve", approve), ("finish", finish)]:
            graph.add_node(name, node)
        graph.add_edge(START, "prepare").add_edge("prepare", "approve")
        graph.add_edge("approve", "finish").add_edge("finish", END)
        return graph.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "approval-demo"}}
    with TemporaryDirectory() as work:
        database = str(Path(work) / "checkpoints.sqlite")
        with SqliteSaver.from_conn_string(database) as saver:
            paused = build(saver).invoke({"draft": "", "approved": False, "result": ""}, config)
            print("[暂停]", paused["__interrupt__"][0].value)
        print("[重新打开数据库] 仍使用相同 thread_id")
        with SqliteSaver.from_conn_string(database) as saver:
            completed = build(saver).invoke(Command(resume=args.decision == "approve"), config)
            print("[继续后]", completed["result"])
            if completed["approved"] != (args.decision == "approve"):
                raise DemoError("恢复后的审批状态与输入不一致。")


if __name__ == "__main__":
    launch(run, __doc__, live=False, configure=options)
