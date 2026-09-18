# 一框架一例子：13 个 Python Agent Demo

**不只是同一段聊天代码换包名：每份脚本只突出一个框架特点。** 先读文件开头的场景，再看 `run()`；公共文件只处理命令行和配置，不隐藏框架调用。

## 选一个想看的场景

|代码|演示场景|重点|是否调用模型|
|---|---|---|---|
|[01 · OpenAI Agents SDK](01_openai_handoff.py)|接待转交订单专家|handoff + 函数工具 + 最终 Agent|需要；平台类还需预先配置|
|[02 · LangGraph](02_langgraph_approval.py)|草稿审批后从 SQLite 继续|图 + interrupt / Command + 检查点|不需要|
|[03 · LangChain](03_langchain_structured.py)|报修描述变为工单对象|create_agent + ToolStrategy / Pydantic|需要；平台类还需预先配置|
|[04 · Deep Agents](04_deepagents_delegate.py)|委派资料员并写虚拟报告|task 子 Agent + 内置文件工具|需要；平台类还需预先配置|
|[05 · Claude Agent SDK](05_claude_readonly.py)|只读代码审查|Read + Hook + 流式消息|需要；平台类还需预先配置|
|[06 · Claude Managed Agents](06_claude_managed.py)|创建云端会话并跟踪事件|托管 Session / Environment / Events|需要；平台类还需预先配置|
|[07 · Google ADK](07_google_adk_pipeline.py)|先写作，再审阅|SequentialAgent + output_key 共享状态|需要；平台类还需预先配置|
|[08 · Microsoft Agent Framework](08_microsoft_typed_flow.py)|解析数量、汇总、展示|类型化 Executor + 消息边 + 最终输出|不需要|
|[09 · DeepSeek Harness](09_deepseek_plugins.py)|通过补丁增加文件工具|官方 Python SDK + profile / patches|需要；平台类还需预先配置|
|[10 · CrewAI](10_crewai_roles.py)|分析员与编辑接力|角色 + Task.context + 顺序 Crew|需要；平台类还需预先配置|
|[11 · LlamaIndex](11_llamaindex_rag.py)|检索虚构办公手册回答问题|Document → 索引 → QueryEngineTool → Agent|需要；平台类还需预先配置|
|[12 · Dify](12_dify_workflow.py)|Python 调用画布工作流|应用 API Key + inputs / outputs|需要；平台类还需预先配置|
|[13 · Coze Studio / Coze](13_coze_workflow.py)|指定已发布的教学流程|Workflow ID + OpenAPI + 平台输出|需要；平台类还需预先配置|

## 先从 LangGraph 跑起：不需要 API Key

在仓库根目录，使用 Python 3.11+。普通 `python` 默认**只预览场景说明**，不安装依赖、不调用模型，也不会打印虚假的成功结果：

```sh
python examples/frameworks/02_langgraph_approval.py
```

每个脚本头部已经写好独立依赖。安装 [uv](https://docs.astral.sh/uv/guides/scripts/) 后，下面才是真正执行框架的命令：

```sh
# 批准分支：草稿 → 暂停 → 重新打开 SQLite → 继续；仅展示，不发送通知。
uv run --script examples/frameworks/02_langgraph_approval.py --run --decision approve

# 拒绝分支。
uv run --script examples/frameworks/02_langgraph_approval.py --run --decision reject

# 微软框架的确定性流程也不需要模型：3,5,2 → 总件数：10。
uv run --script examples/frameworks/08_microsoft_typed_flow.py --run
```

LangGraph 示例只在一个进程内关闭、重开数据库并重新构图，不声称进行了真实进程崩溃测试；检查点也不等于业务操作幂等。

## 再试一个真实 Agent：OpenAI 专家转交

先在本机配置 Key 和支持工具调用的模型。**不要把密钥写入仓库或发到聊天里。**

```sh
# Bash / zsh：替换为你账户实际可用的值。
export OPENAI_API_KEY='你的API密钥'
export OPENAI_MODEL='你的模型ID'
uv run --script examples/frameworks/01_openai_handoff.py --run
```

观察三个位置：`[转交]`、`[专家工具]`、`[最终回答者]`。最后回答者应从接待变成订单专家；未完成转交或查询时脚本会报出未完成，而不是假装成功。

PowerShell 使用 `$env:OPENAI_API_KEY = '...'` 的设置方式，运行命令不变。脚本不自动加载 `.env`；缺少配置时会在导入框架前停止。

## 其他例子怎么准备

|例子|必需环境变量|
|---|---|
|01、03、04、10|`OPENAI_API_KEY`、`OPENAI_MODEL`|
|05 Claude 本地 SDK|`ANTHROPIC_API_KEY`、`ANTHROPIC_MODEL`|
|06 Claude 托管|`ANTHROPIC_API_KEY`、`ANTHROPIC_AGENT_ID`、`ANTHROPIC_ENVIRONMENT_ID`|
|07 ADK|`GOOGLE_API_KEY`、`GOOGLE_MODEL`；脚本明确使用非 Vertex AI 路线|
|09 DeepSeek|`DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`；必须先建立隔离环境|
|11 LlamaIndex|`OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_EMBEDDING_MODEL`|
|12 Dify|`DIFY_BASE_URL`（含 `/v1`）、`DIFY_API_KEY`|
|13 Coze|`COZE_BASE_URL`（不含 `/v1`）、`COZE_API_TOKEN`、`COZE_WORKFLOW_ID`|

06、12、13 不是纯本机库，必须先准备云端对象或已发布工作流。具体节点与输入/输出字段见 [PLATFORMS.md](PLATFORMS.md)，不要只复制 Python 代码而遗漏平台配置。

**09 DeepSeek 特别提醒：**官方 Python SDK 自带运行时，但 `sdk-minimal` 同时提供全访问 Shell。临时目录不是沙箱；必须在无敏感挂载的一次性容器/虚拟机中运行，再加 `--isolated-runtime`。该标志只是确认，不会自动建立隔离。不能在日常宿主机直接试。

## 读代码时重点对比这些差异

01 是把对话交给专家；04 是主 Agent 委派子任务并写虚拟文件；07 是固定两步共享输出；10 是明确角色和 Task 依赖。不要把这四种协作方式混成同一个“多 Agent”。

03 看 Pydantic 工单对象；05 看 Read 前的 Hook 和文件未修改校验；11 看文档先变索引，再作为查询工具交给 Agent。12/13 是真实平台 API 客户端，并未用 Python 模仿一个可视化平台。

所有输入均为合成资料。模型回答可能变化，应观察实际工具调用和产物，不以格式正确替代事实正确。DeepSeek 的文件改好也不单独证明用了指定插件，实际工具路径须看会话事件。

## 测试与版本边界

**已执行 65 项语法、预览、配置保护和 HTTP 本地替身检查；尚未执行任何原生框架或真实模型任务。** 当前环境安装依赖时遇到 PyPI DNS 失败，不能把这些检查说成“13 个 SDK 已全部跑通”。[实际检查记录](../../results/python-demos-validation.json)

```sh
python examples/frameworks/verify.py
```

该命令不安装框架或触发付费调用。完整目录与配置也可读取 [catalog.json](catalog.json)。API 依据与核验范围见 [SOURCES.md](SOURCES.md)。

各脚本使用独立依赖环境；安装声明不是已完成联调的锁文件。大多数包未固定补丁版本，DeepSeek 使用已发布的预览包 `0.1.5rc1`。在联网环境确认跑通后，可执行 `uv lock --script 路径.py` 固定解析版本，升级后重新验证。

在线执行可能计费；LlamaIndex 还会调用 Embedding。Dify／Coze 不自动重试，超时不代表远端没执行。云端 Session、账户侧预算和数据保留需要服务端管理；本地取消或断流不保证远程取消。示例中的步数、超时和估算费用限制并非统一的硬预算。

原研究的 0/420 模型评估和 30 项机制实验保持原样；本目录检查数不计入它们。这些代码是教学入口，不是生产级权限、补偿或安全审计方案。
