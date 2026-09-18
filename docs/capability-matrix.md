# Agent 方案对比：一眼看懂版

> 这张表回答的是“它最适合解决什么”，不是“谁最好”。  
> 本轮真实模型横向测试尚未执行，因此不做成功率、价格和性能排名。

## 核心方案

|方案|把它理解成什么|适合场景|它帮你解决|你仍然必须自己解决|
|---|---|---|---|---|
|**OpenAI Agents SDK**|轻量 Agent SDK|工具型 Agent、快速接入|Agent loop、tools、handoff、session、trace|业务状态、权限、幂等、任务调度|
|**LangGraph**|Agent 工作流运行时|SOP、状态机、暂停恢复|显式流程、checkpoint、状态推进|持久化选型、业务真值、外部操作去重|
|**LangChain**|高层 Agent 开发框架|快速搭 Agent|模型/工具/Agent 抽象|生产流程控制、安全和部署|
|**Deep Agents**|长任务 Harness|研究、文件、复杂上下文|文件、上下文卸载、子Agent|业务权限、沙箱策略、长期事实治理|
|**Claude Agent SDK**|带工具环境的 Agent SDK / Harness|Coding、Research、文件/命令任务|工具、权限接口、hooks、session、subagents|运行环境隔离、业务审计和幂等|
|**Claude Managed Agents**|托管 Agent Runtime|希望减少自建执行环境|托管 session / environment / execution|业务授权、数据治理、成本评估|
|**Google ADK 2.0**|工作流 + Agent 框架|代码化工作流、多种编排|图式/动态/协作流程|事件兼容、外部写入、恢复验证|
|**Microsoft Agent Framework**|企业 Agent / Workflow 框架|已有 Microsoft 技术栈|Agent、workflow、checkpoint|稳定ID、业务幂等、身份和数据治理|
|**DeepSeek Harness**|插件化 Agent Harness|架构研究、隔离 PoC|插件、事件、上下文投影|生产安全、隔离、业务补偿|
|**Dify / Coze Studio**|可视化 Agent 平台|运营/开发共建、快速发布|工作流配置、应用发布、插件|生产权限、版本治理、部署安全|

## 产品层

|产品|最值得观察什么|
|---|---|
|**ChatGPT Work**|如何把复杂任务变成可审阅的完整交付|
|**Claude Code**|编码 Agent 如何读代码、执行命令、修改并验证|
|**Codex**|沙箱、审批、网络权限与代码执行如何结合|
|**Cursor**|交互式 Agent 与人如何不断纠正和协作|
|**Devin**|长期任务委派、环境操作与人工接管|
|**Jules**|仓库任务、计划、执行与最终变更交付|

## 按场景选，而不是按热度选

### 场景 1：简单 Tool Calling

优先从轻量 SDK 开始。

```text
Agent → Tool Gateway → Business Service
```

如果只是查资料、生成内容、调用几个工具，没有必要一开始就搭复杂多 Agent。

### 场景 2：明确业务 SOP

优先看图/工作流体系。

```text
状态 A
 ↓
条件判断
 ↓
Agent
 ↓
规则校验
 ↓
状态 B
```

重点候选：LangGraph、ADK、Microsoft Agent Framework。

### 场景 3：Coding / Research 长任务

优先看 Harness。

```text
Agent
 ├─ Files
 ├─ Shell
 ├─ Search
 ├─ Context
 └─ Subagents
```

重点候选：Claude Agent SDK、Deep Agents，以及相关最终产品。

### 场景 4：低代码 / 团队协同

优先评估 Dify / Coze Studio。

重点不是“LLM 更聪明”，而是：

- 谁能配置；
- 谁能审批；
- 如何上线；
- 如何回滚；
- 如何看日志。

## 选型时真正应该问的 8 个问题

1. 谁管理**业务状态**？
2. 谁管理**对话和 Memory**？
3. 谁保存**工作流进度**？
4. 工具调用前谁做**权限校验**？
5. 外部动作如何做**幂等**？
6. 任务失败后从哪里**恢复**？
7. 用户取消后如何阻止后续**副作用**？
8. 成功与否由什么**独立验收**？

如果这 8 个问题说不清楚，再强的模型也不适合直接进入关键生产链路。

---

## 当前研究边界

本轮已经完成文档与局部源码研究，以及 30 项离线机制实验；真实模型横向对照仍为 **0/420**。

因此，这张表用于：

- 架构讨论；
- PoC 选型；
- 技术路线收敛。

**不用于宣称某个框架在真实任务中排名第一。**

详细证据与原始来源见 [完整能力与证据资料](research-report.md) 和 [来源登记册](../sources/registry.md)。
