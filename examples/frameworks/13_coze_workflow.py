# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28,<1"]
# ///
"""Coze Studio / Coze：指定已发布 Workflow ID → 平台执行 → 返回结果。
看点：Python 选择一个工作流，工作流内部步骤由平台管理。
为兼容已核验的自部署/云端接口，本例采用无输入的固定教学流程，见 PLATFORMS.md。
"""
import json
from _common import DemoError, endpoint, env, launch, post_json


def run(_):
    # COZE_BASE_URL 只填服务根地址，不包含 /v1，也不能用控制台页面地址。
    data = post_json(endpoint("COZE_BASE_URL") + "/v1/workflow/run", env("COZE_API_TOKEN"), {
        "workflow_id": env("COZE_WORKFLOW_ID"),
    })
    if data.get("code") != 0:
        raise DemoError(f"工作流接口返回错误码 {data.get('code')}；检查发布、权限和部署版本。")
    result = data.get("data")
    # 此接口的 data 可能是 JSON 序列化字符串，而非字典。
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            raise DemoError("data 不是约定的 JSON 输出，请检查结束节点设置。") from None
    if not isinstance(result, dict) or not result.get("summary"):
        raise DemoError("缺少 summary；请按 PLATFORMS.md 配置无输入流程和输出字段。")
    print("[工作流]", env("COZE_WORKFLOW_ID"))
    print("[执行结果]", json.dumps(result, ensure_ascii=False, indent=2))
    print("[提醒] 接口路径一致不代表云端和自部署版所有能力、鉴权方式都相同。")


if __name__ == "__main__":
    launch(run, __doc__, ("COZE_BASE_URL", "COZE_API_TOKEN", "COZE_WORKFLOW_ID"))
