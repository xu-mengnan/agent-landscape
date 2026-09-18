# 场景化采用决策

**状态：研究建议，不是生产上线批准。** 不宣布一个“全场景最强框架”。

## ADR-001：先建立业务控制面，再替换Agent编排

决定：将身份授权、业务状态、版本更新、接收方幂等及审计作为独立接口；模型/框架通过适配层使用它们。

理由：框架的Session、checkpoint和guardrail分别解决不同问题。已有文档和离线反例都不足以支持“框架包办事务正确性”。

代价：需要维护少量显式业务接口；收益是框架迁移、模型替换和重试时不重复发明安全规则。撤销条件：仅限完全只读、无持久副作用的小工具，允许采用更简单结构。

## ADR-002：显式业务流程优先验证图式编排

建议将LangGraph列为显式SOP场景候选，同时保留最小实现及ADK/Microsoft等可比较方案。依据是职责匹配，不是已测性能领先。[S06][S13][S14]

验收：非法流转零容忍、旧回调不能覆盖新状态、审批与取消可审计、跨进程重启不重复业务动作。没有满足这些条件前，不切换关键生产链路。

## ADR-003：长任务Harness独立验证

对文件/研究密集任务，Deep Agents与Claude Agent SDK进入单独验证集。先验证上下文卸载、恢复、产物质量、目录隔离及人工接管；不把“长任务”自动理解为多Agent。[S08][S10]

替代方案：小任务保持单Agent+工具。若多Agent没有明显提高质量或可恢复性，保留简单方案。

## ADR-004：DeepSeek Harness先做隔离机制PoC

依据其公开预览/安全声明，将其限于架构学习与无敏感数据的隔离实验。[S18] 重点借鉴插件生命周期、事件投影，而不是直接接入关键写操作。

升级采用条件：固定版本、完成安全审阅、通过权限和恢复测试、明确回滚；不是仅因发布新版本便自动放行。

## ADR-005：平台类按协作与发布流程评估

Dify和Coze Studio围绕配置、发布、权限、版本和运维协作评分，而不与底层SDK按代码行数排名。[S26][S27] 开源版、云版、企业版分别记录，不假设能力相同。

## 决策复查条件

有重大版本/安全声明/执行模型变化，或实际任务数据足以推翻当前假设时复查。复查应绑定相关失败用例，不能只更新功能清单和Logo。


## 证据来源

- [S06] [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)。滚动文档。
- [S13] [Google ADK 2.0](https://adk.dev/2.0/)。2.0版本系列；Python GA 2026-05-19，Go GA 2026-06-30；非最新补丁声明。
- [S14] [Microsoft Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/)。滚动文档；未安装。
- [S08] [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)。滚动文档。
- [S10] [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)。滚动文档。
- [S18] [DeepSeek Harness safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/main/SAFETY.md)。开发者预览安全声明。
- [S26] [Dify Workflow Studio](https://www.dify.ai/workflows)。官方产品说明；未部署。
- [S27] [Coze Studio README](https://github.com/coze-dev/coze-studio/blob/main/README.md)。blob 6f4221d806888d45596156bec6f5599294ea6a2f；读取1–140行。
