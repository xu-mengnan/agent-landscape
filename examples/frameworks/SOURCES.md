# API 核验记录

核验日期：2026-09-19。下面是编写示例所依据的一手接口资料；不是“已实测兼容全部版本”的声明。旧研究基准仍为 2026-09-18。

|脚本|主要官方资料|本次采用的接口|
|---|---|---|
|01|[OpenAI Handoffs](https://openai.github.io/openai-agents-python/handoffs/) · [配置](https://openai.github.io/openai-agents-python/config/)|Agent / Runner / function_tool / handoff / on_handoff|
|02|[LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) · [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)|StateGraph / SqliteSaver / interrupt / Command / thread_id|
|03|[LangChain Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)|create_agent / ToolStrategy / structured_response|
|04|[Deep Agents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents) · [Backends](https://docs.langchain.com/oss/python/deepagents/backends)|create_deep_agent / subagents / task / 默认虚拟文件后端|
|05|[Claude Agent SDK Python](https://code.claude.com/docs/en/agent-sdk/python)|ClaudeSDKClient / tools / HookMatcher / PreToolUse / receive_response|
|06|[Managed Agents Quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart)|beta.sessions.create / events.stream / events.send|
|07|[ADK Sequential](https://adk.dev/agents/workflow-agents/sequential-agents/) · [App](https://adk.dev/apps/)|SequentialAgent / LlmAgent / output_key / App / InMemoryRunner.run_debug|
|08|[Microsoft Executors](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/executors)|executor / WorkflowContext / WorkflowBuilder / output_from / get_outputs|
|09|[DeepSeek Python 教程](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/python-sdk.md) · [SDK 参考](https://github.com/deepseek-ai/deepseek-harness/blob/master/python/sdk/README.md) · [0.1.5rc1 发布包](https://pypi.org/project/deepseek-harness-sdk/0.1.5rc1/)|DeepSeekHarness / profile / patches / RunResult|
|10|[CrewAI Tasks](https://docs.crewai.com/en/concepts/tasks)|Agent / Task.context / Crew / Process.sequential|
|11|[FunctionAgent](https://developers.llamaindex.ai/python/examples/agent/agent_workflow_basic/) · [QueryEngineTool](https://developers.llamaindex.ai/python/framework-api-reference/tools/query_engine/)|Document / VectorStoreIndex / QueryEngineTool / FunctionAgent|
|12|[Dify Workflow 控制器](https://github.com/langgenius/dify/blob/main/api/controllers/service_api/app/workflow.py) · [输出节点](https://docs.dify.ai/en/cloud/use-dify/nodes/output)|POST /workflows/run / blocking / outputs|
|13|[Coze Studio 路由](https://github.com/coze-dev/coze-studio/blob/main/idl/workflow/workflow_svc.thrift) · [OpenAPI 鉴权](https://github.com/coze-dev/coze-studio/blob/main/backend/api/middleware/openapi_auth.go) · [官方 Python 调用例子](https://github.com/coze-dev/coze-py/blob/main/examples/workflow_no_stream.py)|POST /v1/workflow/run / workflow_id|
|运行方式|[uv Scripts](https://docs.astral.sh/uv/guides/scripts/)|PEP 723 / uv run --script / uv lock --script|

## 容易照抄错的边界

Claude SDK 的 `allowed_tools` 是自动批准列表，不是全部可用工具列表；本例用 `tools=["Read"]` 限定集合，再用始终匹配的 PreToolUse Hook 校验唯一文件。`can_use_tool` 并不对每一次自动批准的调用触发，故没有拿它冒充全路径拦截。

DeepSeek 当前已有真实 Python SDK，不能再笼统说它没有 Python 入口。正常 SDK 使用自带运行时；插件管理命令与普通执行的依赖不同。其最小 Profile 风险见 PLATFORMS.md。

LangGraph SQLite 检查点能演示恢复工作流状态，但不能单独保证外部调用幂等。该例使用临时数据库，仅在同一次脚本进程内关闭、重开连接，不声称测试了进程崩溃。

Dify／Coze 示例属于平台 OpenAPI 客户端，必须先有已发布工作流。Cloud／自部署版本的权限和模型配置不能自动互换。

## 可追溯的源码范围

DeepSeek Python 教程 blob：`a14d656171f37a7feea8c091741f2175f9617cd4`；SDK README blob：`bfca3b0dda6c97bbef255815f33ca81121832f4e`。它们是文件 blob，不是提交号。

Dify 控制器读取前225行，blob：`ef6d2a35a57c8ab096c500ef51c378b3792d74d5`；Coze Studio OpenAPI 路由与鉴权检索定位到提交 `fefb05ff27be1da939612fbf9faf5db62583b8ae`。这些局部接口核验不是全仓库审计。

## 测试层次

当前只运行静态/预览/配置/HTTP 替身检查，没有成功安装框架依赖，**没有执行原生 SDK 或模型任务**。不以 Mock Agent 代替原生 Agent 后宣称已经跑通；模型服务、云端 Session、Dify、Coze 和 DeepSeek 原生二进制全部留待有相应环境时验证。
