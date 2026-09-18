# 能力与责任矩阵

不是功能数量排名。U表示未验证，不等于不支持。每行只承载已查证范围；价格、成功率、吞吐没有测量，因此不打分。

|对象|层级|编排证据|状态/上下文证据|安全边界|应用仍需负责|实证状态|本轮判断（I）|
|---|---|---|---|---|---|---|---|
|OpenAI Agents SDK|SDK/Agent循环|Agent/Runner/handoff [S01]|会话历史 [S03]|输入/输出/工具覆盖不同 [S02]|业务幂等、权威状态、运行环境|D+局部S；U运行|工具型服务候选；避免把guardrail当事务授权|
|LangGraph|图编排运行时|显式流程及Agent节点 [S06]|checkpointer/store分开 [S07]|按应用设工具/节点边界|持久后端、状态版本、接收方去重|D+局部S；U运行|明确SOP/恢复场景的候选|
|LangChain|较高层Agent框架|模型/工具/Agent抽象 [S06]|与运行时/应用层配合|不能从抽象层推导完整授权|业务状态、安全与部署|D；U运行|快速Agent开发入口；与LangGraph非互斥|
|Deep Agents|Harness|子Agent与上下文设施 [S08]|文件/卸载/记忆能力 [S08]|按后端/配置核验|沙箱隔离、长期事实治理|D；U运行|长任务/研究执行的候选|
|Claude Agent SDK|SDK/Harness接口|工具与子Agent [S10]|会话接口 [S10]|权限/hooks [S10]|进程、隔离、业务审计|D；U运行|文件/命令型任务机制研究|
|Claude Managed Agents|托管执行服务|托管资源与执行 [S11]|Session/Events [S11]|账户/环境具体核验|数据治理、业务授权与成本|D；Beta；U运行|独立于SDK核算托管取舍|
|Google ADK 2.0|Agent/工作流框架|图式/动态/协作 [S13]|事件迁移需验证 [S13]|应用与运行环境共同承担|事件兼容、取消、外部幂等|D；U运行|代码化工作流的候选|
|Microsoft Agent Framework|Agent/工作流框架|Agent+Workflow [S14]|superstep检查点 [S15]|存储反序列化边界 [S15]|稳定拓扑ID、身份、外部效果|D；U运行|已有相关企业技术栈时验证|
|DeepSeek Harness|插件化Harness|Cordis组合与loop [S16][S17]|持久事件/上下文投影 [S17]|上游明确预览风险 [S18]|隔离、插件治理、业务补偿|D；预览；U运行|隔离PoC；不直接准入关键写链路|
|CrewAI|Flows/Crews|流程+协作 [S24]|本轮未核验具体后端|U|明确过程、状态与重试契约|D；U运行|补充候选，不参加性能排名|
|LlamaIndex|检索/Agent框架|FunctionAgent/AgentWorkflow [S25]|检索/记忆需分层评估|U|数据管线和流程正确性分开|D；U运行|知识密集场景补充候选|
|Dify|可视化平台|工作流节点 [S26]|按部署版本核验|人工节点不等于完整IAM|插件身份、配置治理、回滚|D；U部署|团队配置与发布流程验证|
|Coze Studio|开源可视化平台|Agent/App/Workflow [S27]|开源/商业版分开|公开网络风险提醒 [S27]|部署加固、身份与配置|D；U部署|隔离自部署验证|

源码范围与原始引用见[来源登记册](../sources/registry.md)。本轮30项E实验属于原创可靠性机制，不对应任何一行的SDK成绩。

## 证据来源

- [S01] [OpenAI Agents SDK overview](https://openai.github.io/openai-agents-python/)。滚动文档；未锁定安装包版本。
- [S02] [OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)。滚动文档。
- [S03] [OpenAI Sessions](https://openai.github.io/openai-agents-python/sessions/)。滚动文档。
- [S06] [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)。滚动文档。
- [S07] [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。滚动文档；durable-execution入口重定向至此。
- [S08] [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)。滚动文档。
- [S10] [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)。滚动文档。
- [S11] [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)。Beta；文档列出 managed-agents-2026-04-01。
- [S13] [Google ADK 2.0](https://adk.dev/2.0/)。2.0版本系列；Python GA 2026-05-19，Go GA 2026-06-30；非最新补丁声明。
- [S14] [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/)。滚动文档；未安装。
- [S15] [Microsoft workflow checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)。页面更新标注2026-09-04；Python1.13条目不代表最新版本。
- [S16] [DeepSeek Harness README](https://github.com/deepseek-ai/deepseek-harness/blob/main/README.md)。开发者预览；滚动main。
- [S17] [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/architecture.md)。滚动main；读取架构、事件、turn flow、session log章节；非整库审计。
- [S18] [DeepSeek Harness safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/main/SAFETY.md)。开发者预览安全声明。
- [S24] [CrewAI introduction](https://docs.crewai.com/v1.15.14/en/introduction/index.html)。检索入口重定向文档v1.15.14；不等于最新安装包。
- [S25] [LlamaIndex Agents](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/)。滚动文档；读取Agent/Tools/Multi-Agent章节。
- [S26] [Dify Workflow Studio](https://www.dify.ai/workflows)。官方产品说明；未部署。
- [S27] [Coze Studio README](https://github.com/coze-dev/coze-studio/blob/main/README.md)。blob 6f4221d806888d45596156bec6f5599294ea6a2f；读取1–140行。
