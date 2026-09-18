# Claude Agent SDK 与 Managed Agents：自管执行和托管执行分开核算

**D；未执行SDK、未登录Managed Agents。** SDK和托管服务不能共用一行“支持恢复”的结论。

## 文档确认

D｜Agent SDK提供Python/TypeScript接口及文件、命令等工具设施，可通过权限、hooks、subagents、会话等控制行为；SDK与Claude Code的最终用户入口需要区分。[S10]

D｜Managed Agents文档以Agent、Environment、Session、Events组织托管执行；当前为Beta，文档列出`managed-agents-2026-04-01`头。服务持有会话等状态，不能直接套用无状态模型API的数据处理假设。[S11]

## 责任边界（I）

SDK集成时，应用团队需要回答进程跑在哪里、沙箱如何隔离、磁盘多久保留、凭据如何注入、异常如何回收。托管执行改变了其中部分责任的承担者，但仍需明确会话删除、文件清理、审计导出、网络目的地和外部工具权限。

把SDK封装为内部执行服务时，应避免每次请求都暴露整个宿主机工作目录。按任务分配最小工作区、只注入任务所需凭据，并以服务端身份决定可调用工具。审批应绑定操作参数、用户、有效期和任务版本，而不是一句永久有效的“同意”。

## 复用价值（I）

适合研究成熟的文件/命令工具使用方式、hooks扩展、子任务上下文分离和人工介入。不应以“提供内置工具”推导“业务任务一定更成功”，更不能用产品体验替代SDK可部署性分析。

托管路线可减少部分自建运行设施，但采购比较必须把存储、会话、工具、模型、人工介入和迁移成本放入同一账本。没有实际账户与合同核验时，本报告不给数据驻留或价格承诺。

## 风险与反例（I）

恢复同一session不等于重新获得所有外部授权；插件或工具变更可能导致旧会话重新执行时语义改变。工具具备文件读写不等于具备安全的多租户文件隔离。hooks属于执行扩展点，而不是任意业务补偿机制。

## 实验准入

先在空白合成仓库中完成“读文件→修复小缺陷→运行测试→解释差异”；加入禁止访问的兄弟目录、拒绝的网络目标和失效审批，检查实际环境终态。之后再测试进程退出与session恢复。托管版和SDK版分别保留配置与结果，不能互相抵扣未测项。


## 证据来源

- [S10] [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)。滚动文档。
- [S11] [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)。Beta；文档列出 managed-agents-2026-04-01。
