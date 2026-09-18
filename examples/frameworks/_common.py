"""仅处理命令行、环境配置与 HTTP；没有模拟或替代任何 Agent 框架。"""
import argparse
import asyncio
import inspect
import os
import sys
from urllib.parse import urlsplit


class DemoError(RuntimeError):
    """可直接向演示者说明的配置或验收错误。"""


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise DemoError(f"请先设置环境变量 {name}（不要把密钥写进代码）。")
    return value


def endpoint(name):
    """远程只允许 HTTPS；HTTP 仅允许本机开发地址，不跟随重定向。"""
    value = env(name).rstrip("/")
    url = urlsplit(value)
    if url.username or url.password or url.query or url.fragment:
        raise DemoError(f"{name} 不能包含凭据、查询参数或片段。")
    if not url.hostname or url.scheme not in {"https", "http"}:
        raise DemoError(f"{name} 必须是完整的 HTTP(S) 地址。")
    if url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise DemoError("远程服务请配置 HTTPS；明文 HTTP 只用于本机演示。")
    return value


def post_json(url, key, payload):
    import httpx
    # 不自动重试：超时并不能说明远端工作流没有执行。
    with httpx.Client(timeout=120, follow_redirects=False) as client:
        response = client.post(url, headers={"Authorization": f"Bearer {key}"}, json=payload)
        response.raise_for_status()
        data = response.json()
    if not isinstance(data, dict):
        raise DemoError("接口未返回 JSON 对象，请核对部署版本与 API 地址。")
    return data


def safe_message(error):
    text = str(error)
    for name, value in os.environ.items():
        if name.endswith(("_API_KEY", "_API_TOKEN", "_TOKEN")) and value:
            text = text.replace(value, "[REDACTED]")
    return text


def launch(action, description, required=(), *, live=True, configure=None, argv=None):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="真实执行；在线示例可能产生费用")
    if configure:
        configure(parser)
    args = parser.parse_args(argv)
    print(description.strip(), flush=True)
    if not args.run:
        print("\n[仅预览说明，不是运行结果] 加 --run 才会导入并执行框架。")
        print("需要配置：" + (", ".join(required) or "无 API Key；仍需安装脚本依赖"))
        return
    try:
        for name in required:
            env(name)
        print("\n[真实调用，可能计费]" if live else "\n[真实框架流程，不调用模型]", flush=True)
        result = action(args)
        if inspect.isawaitable(result):
            asyncio.run(result)
    except KeyboardInterrupt:
        print("已中断本地程序；远程托管任务请在服务端确认是否仍在运行。", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"演示未完成：{type(error).__name__}: {safe_message(error)}", file=sys.stderr)
        raise SystemExit(1)
