# Agent Landscape

> **一句话结论：不要先问“哪个 Agent 框架最强”，先问“我们需要谁来负责流程、状态、记忆、权限、恢复和业务写入”。**

这个项目调研当前主流 Agent 框架与产品，目标不是堆功能清单，而是回答三件事：

1. **现在主流方案分别擅长什么？**
2. **哪些能力值得借鉴，哪些不能直接相信？**
3. **如果要落到生产系统，我们下一步应该怎么做？**

研究基准日：**2026-09-18**。当前结论来自官方/上游资料、局部源码核验和原创离线机制实验。真实模型横向对照尚未执行，因此这里不做“谁第一”的排名。

---

## 先看结论

### 1. Agent 框架不是同一种东西

|类型|代表|主要解决什么|
|---|---|---|
|轻量 Agent SDK|OpenAI Agents SDK|模型循环、工具调用、handoff、session、trace|
|工作流 / 图运行时|LangGraph、Google ADK、Microsoft Agent Framework|流程、状态、暂停、恢复、显式SOP|
|Agent Harness|Claude Agent SDK、Deep Agents、DeepSeek Harness|文件、命令、上下文、子Agent、执行环境|
|平台型产品|Dify、Coze Studio|可视化配置、发布、团队协作|
|最终用户产品|Claude Code、Codex、Cursor、Devin、Jules、ChatGPT Work|把能力打包成可直接使用的工作方式|

**所以不能把它们放在一张“功能数量排行榜”里。**

### 2. 最值得借鉴的 5 个设计

**① 业务状态和 Agent 状态分开**  
聊天历史、Memory、Checkpoint、订单/支付状态不是一回事。关键业务事实应该由业务系统掌握。

**② 高风险工具在执行点做权限校验**  
Prompt 里写“不要越权”不够。真正执行发送、修改、发布时，需要服务端再次检查身份、参数和审批。

**③ 恢复能力必须配合幂等**  
Agent 能恢复，不代表外部动作不会重复。典型场景是“消息已经发送，但返回结果丢失”，此时重试必须靠稳定操作ID和接收方去重。

**④ 多 Agent 不是越多越好**  
只有任务可拆、上下文需要隔离、结果可以可靠合并时，多 Agent 才有价值。否则会增加成本、冲突和排障难度。

**⑤ 评测看最终结果，不看 Agent 自报**  
“任务完成了”不能作为成功标准。应该检查真实文件、数据库状态、测试结果、工具副作用和审批记录。

### 3. 当前比较适合的技术路线

|场景|优先研究方向|
|---|---|
|简单工具调用、轻量服务|OpenAI Agents SDK 等轻量 SDK|
|明确 SOP、状态流转、暂停恢复|LangGraph / ADK / Microsoft Agent Framework|
|长任务、文件、命令、研究执行|Claude Agent SDK / Deep Agents 等 Harness|
|业务人员参与配置、可视化发布|Dify / Coze Studio|
|编码或完整工作交付|Claude Code / Codex / Cursor / Devin / Jules / ChatGPT Work|

这不是性能排名，而是**按职责匹配**。

---

## 对生产系统最重要的三个落地方向

### A. Memory：不要只追求“记得更多”

重点应该是：

- 用户纠正后，旧信息不能继续生效；
- 权威业务状态不能被用户一句话或摘要覆盖；
- Memory 要有来源、版本、过期时间和删除机制；
- 压缩和向量检索不能破坏关键约束。

### B. 对话后的异步 Agent：防止旧结果污染新状态

典型流程：

```text
一轮对话结束
  → 异步生成
  → 读取当前状态
  → 规则校验
  → 比较 turn_id / state_version
  → 合法才写入
```

这样可以避免旧任务回来后覆盖新一轮状态。

### C. 大规模异步执行：Agent 和传统后端工程必须结合

需要的不是“让模型自己重试”，而是：

```text
任务表 / 队列
  → 幂等
  → 限流
  → 重试
  → 死信 / 对账
  → 发送前再次检查状态和权限
```

---

## 这次实际做了什么

- 核验 **31 项**官方/上游来源；
- 研究 **6 个核心技术体系**；
- 整理 **6 款 Agent 产品**；
- 补充 CrewAI、LlamaIndex、Dify、Coze Studio；
- 局部阅读 OpenAI Guardrail 与 LangGraph Checkpointer 源码；
- 实际运行 **30 项离线机制检查**；
- 设计 **35 个真实模型评估用例**。

> **重要边界：真实模型对照目前是 0/420，商业产品原生任务也尚未实测。**
>
> 30 项检查验证的是幂等、恢复、状态冲突、权限顺序等工程机制，**不是 Agent 模型成功率**。

---

## 推荐阅读顺序

如果只有 **5 分钟**：

1. [老板/同事版摘要](docs/executive-summary.md)
2. [简化能力矩阵](docs/capability-matrix.md)
3. [三个业务 PoC](docs/decisions/business-pocs.md)

如果要做技术评审：

- [完整研究报告](docs/research-report.md)
- [八层架构拆解](docs/architecture.md)
- [安全与成本](docs/security-and-cost.md)
- [采用决策](docs/decisions/adoption.md)
- [来源登记册](sources/registry.md)

如果要继续做真实测评：

- [35 个评估用例](benchmarks/README.md)
- [离线实验结果](results/experiment-report.md)

---

## 项目最终想回答的问题

> **一个真正可落生产的 Agent 系统，模型应该负责什么，框架应该负责什么，而哪些事情必须仍然交给传统后端系统？**

当前研究给出的方向是：

```text
模型：理解、生成、规划
框架：编排、上下文、工具调用、执行过程
业务系统：权限、事实状态、幂等、审计、最终写入
```

三层分清楚，比选择“最热门框架”更重要。
