# /// script
# requires-python = ">=3.11"
# dependencies = ["anthropic"]
# ///
"""Claude Managed Agents：建立云端 Session → 投递事件 → 接收执行事件。
看点：任务运行在托管环境，不是本地 Agent SDK，也不是一次 messages.create。
需预建无危险工具且有限额的 Agent / Environment；会创建真实云端 Session。
"""
import time
from _common import DemoError, env, launch


def run(_):
    from anthropic import Anthropic

    with Anthropic(timeout=30, max_retries=0) as client:
        if not hasattr(client.beta, "sessions"):
            raise DemoError("当前 anthropic 包没有 beta.sessions，请按官方 quickstart 升级。")
        session = client.beta.sessions.create(
            agent=env("ANTHROPIC_AGENT_ID"), environment_id=env("ANTHROPIC_ENVIRONMENT_ID"),
            title="agent-landscape 教学演示",
        )
        print("[云端 Session]", session.id, flush=True)  # 出错时据此查运行记录。
        print("[生命周期] 断流/异常不会自动取消或删除这个 Session。", flush=True)
        deadline = time.monotonic() + 120
        idle, received = False, False
        with client.beta.sessions.events.stream(session.id) as stream:
            client.beta.sessions.events.send(session.id, events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": "不调用工具，用三句话解释什么是任务交接。"}],
            }])
            for event in stream:
                print("[事件]", event.type)
                if event.type == "agent.message":
                    received = True
                    for block in event.content:
                        if block.type == "text":
                            print(block.text)
                if event.type == "session.status_idle" and received:
                    idle = True
                    break
                if time.monotonic() >= deadline:
                    raise DemoError("超过本地观察窗口，请到服务端检查 Session；断流不等于取消。")
        if not idle:
            raise DemoError("未观察到回复后的 idle 事件，请查询 Session 状态。")
        print("[注意] Session 仍保存在服务端，请按账户保留策略处理。")


if __name__ == "__main__":
    launch(run, __doc__, ("ANTHROPIC_API_KEY", "ANTHROPIC_AGENT_ID", "ANTHROPIC_ENVIRONMENT_ID"))
