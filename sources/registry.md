# 来源登记册

核验基准：2026-09-18。全部为官方文档、官方工程文章或上游仓库；不是新闻聚合。D=文档，S=有明确文件和范围的源码阅读。访问日期不是发布日期；滚动页面不能证明某个安装包版本已实现全部能力。

|ID|来源|证据|版本/读取边界|支持的事实|
|---|---|---|---|---|
|S01|[OpenAI Agents SDK overview](https://openai.github.io/openai-agents-python/)|D|滚动文档；未锁定安装包版本|Agent、Runner、handoff、tools 与 SDK 定位|
|S02|[OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)|D|滚动文档|输入检查并行默认值、首尾 Agent 覆盖与工具检查边界|
|S03|[OpenAI Sessions](https://openai.github.io/openai-agents-python/sessions/)|D|滚动文档|会话历史、恢复时同一 session、与服务端 continuation 的互斥约束|
|S04|[OpenAI Tracing](https://openai.github.io/openai-agents-python/tracing/)|D|滚动文档|默认追踪、敏感数据采集配置、导出处理器|
|S05|[OpenAI guardrail.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/guardrail.py)|S|blob 07475c8183835ae42d9242bcf0f1bcdb93732ed6；阅读1–220行|InputGuardrail 默认 run_in_parallel=True；检查结果与执行函数接口|
|S06|[LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)|D|滚动文档|LangGraph、LangChain、Deep Agents 的职责分层|
|S07|[LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)|D|滚动文档；durable-execution入口重定向至此|checkpointer 与 store、线程范围、内存与持久后端|
|S08|[Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)|D|滚动文档|上下文卸载、子 Agent、文件系统、可选 planning/skills|
|S09|[LangGraph InMemorySaver implementation](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/memory/__init__.py)|S|blob 0f0719c61fe64efddd0e1837eefd94eff23d39f9；阅读1–130行|默认 defaultdict 内存保存；源码说明调试测试用途|
|S10|[Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)|D|滚动文档|SDK、工具、权限、hooks、会话与托管产品区分|
|S11|[Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)|D|Beta；文档列出 managed-agents-2026-04-01|托管执行、Agent/Environment/Session/Events 资源|
|S12|[Claude Code overview](https://code.claude.com/docs/en/overview)|D|滚动产品文档；未登录产品|终端/IDE/桌面/浏览器入口、文件与命令、工作流程|
|S13|[Google ADK 2.0](https://adk.dev/2.0/)|D|2.0版本系列；Python GA 2026-05-19，Go GA 2026-06-30；非最新补丁声明|图式/动态/协作工作流与1.x迁移风险|
|S14|[Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/)|D|滚动文档；未安装|Agent、工作流、会话与 AutoGen/Semantic Kernel 迁移定位|
|S15|[Microsoft workflow checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)|D|页面更新标注2026-09-04；Python1.13条目不代表最新版本|superstep检查点、恢复拓扑标识、反序列化边界|
|S16|[DeepSeek Harness README](https://github.com/deepseek-ai/deepseek-harness/blob/main/README.md)|D|开发者预览；滚动main|Cordis、插件组合、兼容性变更提示|
|S17|[DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/architecture.md)|D|滚动main；读取架构、事件、turn flow、session log章节；非整库审计|持久会话事实、运行时事件、上下文投影与崩溃限制|
|S18|[DeepSeek Harness safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/main/SAFETY.md)|D|开发者预览安全声明|未安全审计，不应按安全/生产就绪软件对待|
|S19|[Get started with ChatGPT Work](https://learn.chatgpt.com/docs/get-started-with-work)|D|滚动产品文档；未开展独立产品实验|以可审阅产物为目标、工具和交互、入口差异|
|S20|[Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)|D|官方工程文章；非本项目部署记录|沙箱、审批、网络与日志的不同职责|
|S21|[Cursor Agent overview](https://cursor.com/docs/agent/overview)|D|滚动产品文档；未登录产品|编辑/终端/搜索、本地检查点与Git相互独立|
|S22|[Devin introduction](https://docs.devin.ai/get-started/devin-intro)|D|滚动产品文档；未登录产品|Shell/IDE/Browser、人工接管与任务交付；文档提醒行为可能变化|
|S23|[Jules getting started](https://jules.google/docs/)|D|页面标注experimental；未登录产品|GitHub集成、编码任务；不推断商业版或最新状态|
|S24|[CrewAI introduction](https://docs.crewai.com/v1.15.14/en/introduction/index.html)|D|检索入口重定向文档v1.15.14；不等于最新安装包|Flows 与 Crews 的组合定位|
|S25|[LlamaIndex Agents](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/)|D|滚动文档；读取Agent/Tools/Multi-Agent章节|FunctionAgent、QueryEngineTool、AgentWorkflow|
|S26|[Dify Workflow Studio](https://www.dify.ai/workflows)|D|官方产品说明；未部署|可视化工作流、知识/工具/代码/人工节点与发布|
|S27|[Coze Studio README](https://github.com/coze-dev/coze-studio/blob/main/README.md)|D|blob 6f4221d806888d45596156bec6f5599294ea6a2f；读取1–140行|开源平台范围、Go后端、Eino致谢、公开网络部署风险提示|
|S28|[Model Context Protocol specification](https://modelcontextprotocol.io/specification/2026-07-28)|D|latest入口解析为2026-07-28|工具/资源/提示接口；版本及可选扩展必须分别核验|
|S29|[Agent2Agent protocol](https://a2a-protocol.org/latest/)|D|滚动规范入口；未做互操作测试|跨独立Agent发现、任务及结果交换|
|S30|[Agent Skills](https://agentskills.io/home)|D|滚动规范入口|SKILL.md、元数据、渐进式加载及附属资源|
|S31|[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)|D|2026-01-09工程文章|任务、重复试验、轨迹、评分器与环境终态区分|

## 证据限制

记录可回访URL，并为两段源码保存实际返回的blob SHA。未归档整页内容，也没有将动态页面锁定为一个不可变版本。未读取完整源码库、未核验全部语言/套餐能力，未采集商业产品账户数据。报告不引用搜索返回的非官方镜像、营销排名或过期CLI使用示例。

两条源码记录是局部阅读，不能替代安全审计。Coze README 即使有blob SHA也仍标记D，不把README当源码测试。
