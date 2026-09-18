# Agent Landscape

调研现在主流 Agent 框架和产品：**不只列功能，而是说明架构、执行责任、失败边界和采用条件。**

研究基准日：**2026-09-18**。本轮为官方资料研究＋局部源码核验＋原创离线机制实验。

> **完成边界**：31项来源；六个核心技术体系；六款产品资料卡；四个补充项目；两处局部源码核验；30项离线检查通过。真实模型对照 **0/420**，原生产品任务未测。30/30是代码检查结果，**不是Agent任务成功率**。发布与核验记录见[交付状态](docs/delivery-status.md)。

## 从这里阅读

|内容|入口|
|---|---|
|完整研究结论、证据与局限|[详细报告](docs/research-report.md)|
|各方案承担什么，不承担什么|[能力矩阵](docs/capability-matrix.md) / [CSV](docs/capability-matrix.csv)|
|八层分析和状态责任|[架构拆解](docs/architecture.md)|
|如何采纳，如何回滚|[采用决策](docs/decisions/adoption.md) / [三个业务PoC](docs/decisions/business-pocs.md)|
|真实执行了什么|[实验结果](results/experiment-report.md) / [原始JSON](results/offline-results.json)|
|还未执行的模型任务|[35例任务集](benchmarks/README.md) / [覆盖表](benchmarks/coverage.md)|
|事实来自哪里|[来源登记册](sources/registry.md) / [源码读取记录](docs/source-review.md)|
|安全、费用与证据标准|[安全与成本](docs/security-and-cost.md) / [方法](docs/research-methodology.md)|
|如何入库|[发布说明](PUBLISH.md)|

## 核心技术体系

[OpenAI Agents SDK](docs/frameworks/openai-agents-sdk.md) · [Claude SDK/Managed Agents](docs/frameworks/claude-agent-sdk.md) · [LangChain/LangGraph/Deep Agents](docs/frameworks/langchain-stack.md) · [Google ADK2.0](docs/frameworks/google-adk.md) · [Microsoft Agent Framework](docs/frameworks/microsoft-agent-framework.md) · [DeepSeek Harness/Cordis](docs/frameworks/deepseek-harness.md)

[补充：CrewAI、LlamaIndex、Dify、Coze Studio](docs/frameworks/supplementary.md) · [MCP/A2A/Skills](docs/protocols-and-skills.md)

## 产品研究

[ChatGPT Work](docs/products/chatgpt-work.md) · [Claude Code](docs/products/claude-code.md) · [Codex](docs/products/codex.md) · [Cursor](docs/products/cursor.md) · [Devin](docs/products/devin.md) · [Jules](docs/products/jules.md)

这些卡片是官方资料分析与待执行验收任务，不是假装登录后的使用测评。

## 复现实验

```sh
python scripts/run_checks.py
python scripts/validate_bundle.py
```

Python3.10+，无第三方依赖、无模型调用、无真实业务动作。真实子进程退出、独立SQLite持久化、并发去重、版本冲突、审批/取消与记忆策略均使用合成数据。

## 本轮推荐的阅读结论

先建立业务状态、权限、幂等及审计边界，再选择Agent循环或图编排。长任务Harness和最终产品分开验证；以可检查终态而非自报完成判分。预览状态、依赖版本和未测项必须影响采用决策。

## 维护规则

D=官方文档；S=具体源码；E=实际执行；I=分析判断；U=未验证。新增能力必须附来源/版本；新增成绩必须附原始结果。不得提交真实用户会话、内部提示词、生产接口、密钥或原始生产Trace。

重大版本或安全变化发生时，先更新证据和受影响用例，再更新采用建议；本仓库没有开启自动监控或付费测试。
