# 平台型示例的前置准备

普通 SDK 例子可以在 Python 中直接定义 Agent；托管服务和可视化平台还需要服务端对象。下面只创建最小教学场景，不接真实支付、通知、生产数据库或内部知识库。

## 06 · Claude Managed Agents

按[官方 quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart)在有权限的账户中预建 Agent 和 Environment，并记录返回的 ID。示例不替你自动创建一组长期基础资源。

Agent 配置短回复、使用你有权限的模型，不挂载工具/连接器、真实仓库、业务凭据或敏感目录；Environment 按需限制网络并设置账户侧用量限制。该示例只发一个合成文本问题，不需要完整的 bash/web 工具包。具体可配置项以你的账户和服务版本为准。

设置 `ANTHROPIC_API_KEY`、`ANTHROPIC_AGENT_ID`、`ANTHROPIC_ENVIRONMENT_ID` 后运行 `06_claude_managed.py --run`。脚本只创建一个 Session，打印其 ID 后订阅事件。SDK 按官方 quickstart 处理 Managed Agents 的 beta 头；不要手工把普通 Messages API 的参数拼成 Session 参数。

这会产生云端任务/资源费用，脚本不会自动删除 Session。异常或本地断开后，请在服务端确认执行状态并按保留策略清理。文本中写“不要调用工具”不是权限控制，必须提前从服务端移除不需要的工具。

## 12 · Dify：有输入的工作流

在你的 Dify 部署创建 **Workflow，而不是 Chatflow**：

`用户输入 topic（字符串） → LLM → 输出 summary（字符串）`

LLM 节点使用已配置的模型；提示词填写“根据主题给出三句中文说明”，再通过画布变量选择器引用 `topic`。输出节点把 LLM 的文本映射到 `summary`。先在画布中测试，再发布。

在该应用的 API 页面创建应用 API Key，并复制 Service API Base URL。云端常见形式为 `https://api.dify.ai/v1`；自部署以页面实际地址为准。设置 `DIFY_BASE_URL`（包含 `/v1`）和 `DIFY_API_KEY`。

脚本调用 `POST /workflows/run`，传入 `inputs.topic` 和 `response_mode=blocking`；应用 Key 已确定目标应用，因此本例不再传 Workflow ID。返回必须为成功状态且包含 `data.outputs.summary`。

输入字段不匹配、模型未配置、用 Chatflow Key 或没有发布都会失败。请求超时后先看运行日志，不能把重复 POST 当安全恢复策略。

## 13 · Coze Studio / Coze：无输入的已发布工作流

为避免不同版本对 `parameters` 表示方式的差异，本例选择**开始节点不要求输入**的流程：

`开始（无必填输入） → LLM（固定教学问题） → 结束（返回变量 summary）`

LLM 固定提示为“用三句中文解释 Agent 为什么需要工具”，使用你的部署已配置的模型。结束节点选择返回变量模式，`summary` 映射 LLM 文本。测试后发布，并为调用身份授予该工作流的运行权限。

设置 `COZE_BASE_URL` 为服务根地址（例如自己的 HTTPS 域名，不含 `/v1`），`COZE_API_TOKEN` 为该服务颁发的凭据，`COZE_WORKFLOW_ID` 为发布后的 ID。不要混用云端 Token 与自部署地址，也不要把工作空间 ID 当工作流 ID。

上游 Coze Studio 在 `idl/workflow/workflow_svc.thrift` 暴露 `POST /v1/workflow/run`，相应鉴权中间件处理该 OpenAPI 路由；本例直接使用 Bearer 请求，检查 `code == 0` 并解析 `data`。云端和自部署的身份配置、版本与其他能力仍需要分别核验。运行同一固定流程两次也可能两次计费。

先在本机部署试验时允许 `http://localhost:端口`；远程必须使用 HTTPS。凭据的创建和具体权限以所用部署的说明为准；本例没有测试任何真实 Coze 服务。

## 09 · DeepSeek Harness：隔离要求不是可选的注释

[官方 Python 教程](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/python-sdk.md)说明，`deepseek-harness-sdk` 自带匹配的原生运行时，无需系统 Node.js。`sdk-minimal` 的 **Shell 使用 danger-full-access**，能修改运行环境可见的任何路径；`cwd`、临时目录、`dsh_home` 均不能把它变成安全沙箱。

本例用官方 `patches` 接口给最小 Profile 加入 `str_replace_editor`，但没有删除原有 Shell。运行前必须使用一次性容器或虚拟机，不挂载用户家目录、SSH、Git 凭据、生产目录或 Docker socket，只使用限额模型 Key。`--isolated-runtime` 仅是显式确认标志，程序无法据此证明环境安全。

在已隔离且有 uv 的环境中运行：

```sh
uv run --script examples/frameworks/09_deepseek_plugins.py --run --isolated-runtime
```

仅设置 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`。脚本固定操作一个生成的测试文件，不接受任意项目任务。官方文档还提示会话日志后缀默认可能随模型请求上传，因此不能在这个演示环境放敏感内容。独立临时 Home 会在退出时清理本地日志；这不删除提供方已经收到的数据，也不意味着模型调用不会计费。

预览 SDK 变化较快。本例的文件终态验收能确认修改结果，但不能单独证明模型一定使用了插件而没有使用 Shell；真实工具路径以 `RunResult.events` 为准。
