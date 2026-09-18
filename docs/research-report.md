# 2026 Agent 框架与产品调研报告

**基准日：2026-09-18｜成果类型：证据研究＋局部源码核验＋原创离线实验**

> 本轮核验31项官方/上游来源，研究六个核心技术体系、六款产品和四个补充项目。实际执行30项零模型调用的机制检查。真实模型420次对照计划及商业产品任务尚未运行；首次GitHub写入曾被集成403拒绝；恢复授权后的发布状态单独记录。

## 一、结论：先回答责任边界，不先选“最强框架”

本轮最重要的结论是：框架可减少模型调用、工具编排和上下文设施的建设工作，但不应默认承担业务授权、状态真值和外部操作唯一性。不同产品中的“记忆”“恢复”“审批”经常处于不同层次，必须拆开验证。

建议用两张表决策：第一张列出任务需要哪些责任，第二张列出候选技术已验证承担哪些责任。未覆盖部分要么由应用补足，要么成为采用门槛；不因功能多便自动胜出。

本轮没有证明任何框架在真实任务成功率、价格或性能上领先。提供的是机制证据、可重复的故障反例以及基于场景的候选选择。

## 二、生态如何分类

核心技术线包括OpenAI Agents SDK；Claude Agent SDK与Managed Agents；LangChain/LangGraph/Deep Agents；Google ADK2.0；Microsoft Agent Framework；DeepSeek Harness/Cordis。不同层次的对象不使用同一个笼统“Agent框架”标签。

例如LangGraph官方区分较高层框架、编排运行时与Harness，Claude文档也区分自管SDK与托管执行。[S06][S10][S11] 这决定了部署、存储、运行环境和扩展责任不能直接横向打勾。

产品线覆盖ChatGPT Work、Claude Code、Codex、Cursor、Devin、Jules。它们的文档用于研究交付与人机协作模式；本轮没有进入账户执行真实对照，产品研究卡均标记U运行。

补充项目CrewAI、LlamaIndex、Dify和Coze Studio分别用于拓宽协作、检索和平台控制面的观察，不代表市场份额筛选结果。

## 三、五个有直接证据的工程发现

### 1. 输入检查不一定先于工具执行

OpenAI文档和局部源码共同确认InputGuardrail默认并行执行，并区分不同工具检查范围。[S02][S05] 工程含义：检查失败可以中止后续步骤，却不自动撤销已提交动作；高风险工具应在执行点独立核验权限和参数。

### 2. “保存状态”不是统一的持久恢复承诺

LangGraph将checkpointer与store分开；默认InMemorySaver局部源码使用内存容器。[S07][S09] Microsoft的恢复还涉及拓扑和执行器标识一致性。[S15] 工程含义：需要明确后端、恢复版本、重放位置和外部副作用，不能把Demo中的持久化词语当生产保障。

### 3. Harness的价值在模型周围的执行设施

Deep Agents公开说明上下文/文件/子Agent设施；DeepSeek架构把插件、运行时事件与持久会话事实分开。[S08][S17] 工程含义：可以局部借鉴上下文投影、执行点拦截和子任务隔离，不必为了一个能力全部迁移。

### 4. 预览状态必须进入采用决策

DeepSeek的上游安全声明明确其尚未安全审计、不能按生产就绪系统对待。[S18] 本轮据此建议隔离PoC，不将它直接准入关键写链路。该判断与模型聪明程度无关，也不代表所有其他框架已经通过生产审计。

### 5. 协议互通不等于授权或事务完成

MCP、A2A、Skills分别覆盖能力接口、跨Agent协作和任务说明/资源包装。[S28][S29][S30] 工程含义：接入协议之后仍需身份、工具范围、版本、取消、幂等和审计；“支持MCP”不能单独成为选型结论。

## 四、实际做了哪些实验

实验仅使用Python标准库和合成数据，不调用模型、不安装SDK、不发送真实通知。两个独立SQLite文件分别模拟任务意图和下游效果的持久化边界。

|实验|对照与结果|能够支持的结论|
|---|---|---|
|返回丢失后重试|朴素方案2次效果；稳定键+接收方原子去重保持1次|仅有重试会重复，去重责任要落到接收方|
|真实子进程硬退出|退出码23；下游已生效，任务仍pending；新进程恢复后done且效果仍1次|指定故障窗口下的本示例可恢复|
|并发重复请求|16次相同请求只有一次新增效果|本地SQLite原子去重在该并发条件成立|
|状态冲突|两个相同版本写者只有一个胜出；旧回调被拒|CAS与合法流转能保护该模型|
|授权顺序|事后拒绝仍有1次效果；执行前拒绝为0次|授权位置很重要|
|记忆策略|版本、来源、TTL、租户和删除墓碑检查通过|所定义KV策略按代码工作|

30项检查全部通过，其中3项负对照通过的含义是“成功暴露了预期的不安全结果”。**30/30不是Agent任务成功率。** 原始日志、逐项JSON和限制详见[实验报告](../results/experiment-report.md)。

这些测试没有模拟网络分区、数据库集群、宿主断电、真实模型、向量检索或厂商内部执行路径。结果不能外推为分布式exactly-once或生产可靠性认证。

## 五、框架怎样选

需要明确SOP、暂停与状态进度时，可将图式运行时列为候选；需要小型工具循环时，可以保留轻量SDK；需要文件/研究类长任务时，单独验证Harness；需要团队配置与发布时，评估平台控制面。

具体建议及撤销条件见[采用决策](decisions/adoption.md)。它们是基于职责匹配的工程判断，不是性能排名。现有业务状态、幂等和权限服务应成为稳定边界，避免随模型框架一起换掉。

## 六、对业务落地意味着什么

对话记忆先验证纠正、来源、过期和删除，再追求Token下降。后置建议先保证轮次/状态版本有效，再比较生成质量。批量通知先保证发送前权限与接收方去重，再扩大并发。

三份通用PoC设计包含输入、数据契约、异常、指标及回滚，见[业务验证设计](decisions/business-pocs.md)。它们使用合成场景，不表示已经改动任何现有生产系统，也没有编造收益提升数字。

## 七、还缺什么证据

35例真实模型任务已经写成结构化文件，但尚未接通厂商SDK适配器或运行。模型版本、预算、账号、工具权限尚未冻结，不能给出420次实测结果。商业产品未登录测试；托管服务的数据治理、套餐费用和实际可用性需要独立核验。

未来正式执行时应保留失败样本、完整终态和预算；比较同一模型时公开适配差异；比较原生产品时记录入口差异。小样本接近时可得出“暂不能区分”，不必强行排序。[S31]

## 八、GitHub交付状态

初次创建分支、文件和Issue均被GitHub返回403。恢复授权后已重新读取仓库基线、成功创建研究分支并复跑离线检查；最新提交和PR以[交付状态](delivery-status.md)及[发布记录](../results/github-publish-status.json)为准。发布操作不改变本报告的研究基准日或未执行实验范围。

## 阅读导航

[能力矩阵](capability-matrix.md) · [八层架构](architecture.md) · [方法与边界](research-methodology.md) · [源码核验](source-review.md) · [安全与成本](security-and-cost.md) · [来源登记册](../sources/registry.md)


## 证据来源

- [S06] [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)。滚动文档。
- [S10] [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)。滚动文档。
- [S11] [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)。Beta；文档列出 managed-agents-2026-04-01。
- [S02] [OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)。滚动文档。
- [S05] [OpenAI guardrail.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/guardrail.py)。blob 07475c8183835ae42d9242bcf0f1bcdb93732ed6；阅读1–220行。
- [S07] [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。滚动文档；durable-execution入口重定向至此。
- [S09] [LangGraph InMemorySaver implementation](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/memory/__init__.py)。blob 0f0719c61fe64efddd0e1837eefd94eff23d39f9；阅读1–130行。
- [S15] [Microsoft workflow checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)。页面更新标注2026-09-04；Python1.13条目不代表最新版本。
- [S08] [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)。滚动文档。
- [S17] [DeepSeek Harness architecture](https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/architecture.md)。滚动main；读取架构、事件、turn flow、session log章节；非整库审计。
- [S18] [DeepSeek Harness safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/main/SAFETY.md)。开发者预览安全声明。
- [S28] [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2026-07-28)。latest入口解析为2026-07-28。
- [S29] [Agent2Agent protocol](https://a2a-protocol.org/latest/)。滚动规范入口；未做互操作测试。
- [S30] [Agent Skills](https://agentskills.io/home)。滚动规范入口。
- [S31] [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)。2026-01-09工程文章。
