# Agent 框架与产品调研：老板 / 同事版

## 一句话结论

**主流 Agent 技术已经能够很好地解决“模型怎么调用工具、怎么编排流程、怎么处理长任务”，但真正上生产时，权限、业务状态、幂等、审计和最终写入仍然不能交给模型自动决定。**

因此，这次调研最重要的结论不是“选哪一个框架”，而是：

> **先建立稳定的业务控制面，再根据场景选择 Agent SDK、图运行时或 Harness。**

---

## 为什么要做这次调研

现在市面上同时出现了：

- OpenAI Agents SDK
- Claude Agent SDK / Managed Agents
- LangGraph / Deep Agents
- Google ADK
- Microsoft Agent Framework
- DeepSeek Harness
- Dify / Coze Studio
- Claude Code / Codex / Cursor / Devin / Jules

如果只看宣传页，几乎每家都支持：

- Tool Calling
- Memory
- Multi-Agent
- Workflow
- Context
- Human-in-the-loop
- MCP

但这些词背后的含义差别很大。

例如：

- “支持 Memory”可能只是保存聊天记录；
- “支持恢复”可能只是恢复工作流，不保证外部消息不会重复发送；
- “支持 Guardrail”不代表所有工具都经过同样的授权检查；
- “支持 Multi-Agent”也不代表复杂任务一定比单 Agent 更好。

所以真正需要研究的是：**能力背后的责任边界。**

---

## 主流方案怎么理解

### 第一类：轻量 Agent SDK

代表：**OpenAI Agents SDK**

适合：

- 工具调用；
- Agent handoff；
- session；
- tracing；
- 自己已经有业务后端，只需要一层 Agent 能力。

优势是简单、容易接入。

但业务状态、事务、权限和异步任务仍然需要自己的系统承担。

---

### 第二类：工作流 / 图运行时

代表：

- **LangGraph**
- **Google ADK**
- **Microsoft Agent Framework**

适合：

- 明确 SOP；
- 多步骤业务流程；
- 人工审批；
- 暂停 / 恢复；
- 状态机；
- 需要知道“当前执行到哪一步”的任务。

这类方案更接近：

```text
业务流程引擎
    +
LLM
```

对于企业 Agent，是非常重要的一条路线。

---

### 第三类：Agent Harness

代表：

- **Claude Agent SDK**
- **Deep Agents**
- **DeepSeek Harness**

Harness 可以简单理解成：

> **围绕模型搭建的一整套执行设施。**

包括：

- 文件；
- Shell；
- 工具；
- 上下文；
- 子 Agent；
- 权限；
- Session；
- 执行环境。

适合：

- Coding Agent；
- Research Agent；
- 长任务；
- 文件密集型任务；
- 需要自主探索的任务。

---

### 第四类：平台型产品

代表：

- **Dify**
- **Coze Studio**

重点价值不是“模型能力更强”，而是：

- 可视化配置；
- 团队协作；
- 工作流发布；
- 插件管理；
- 运营和开发共同参与。

比较这类产品时，应该重点看版本管理、权限、发布、回滚和运维，而不是和 SDK 比谁代码少。

---

### 第五类：最终用户 Agent 产品

代表：

- Claude Code
- Codex
- Cursor
- Devin
- Jules
- ChatGPT Work

这些产品值得研究的是：

> **一个完整 Agent 产品应该如何让用户委派任务、纠正任务、审批风险动作、查看过程和验收结果。**

它们更多给我们产品设计启发，而不是直接作为底层框架选型依据。

---

## 5 个最值得借鉴的设计

### 1. 状态分层

必须区分：

```text
聊天记录
Memory
Workflow Checkpoint
业务状态
运行环境
审计日志
```

这几个东西不能放在一个“Memory”概念里。

例如支付状态应该来自支付系统，而不是模型摘要。

---

### 2. 工具调用必须有执行点授权

一个 Agent 可能决定：

> “发送消息。”

但最终执行服务还要判断：

- 当前用户有没有权限？
- 参数是不是本次批准的？
- 任务是否已经取消？
- 状态是否已经变化？

因此正确架构应该是：

```text
Agent 提议操作
     ↓
业务授权层
     ↓
真实执行
```

而不是：

```text
Agent → 直接修改业务
```

---

### 3. Checkpoint + 幂等

Agent 世界里非常常见的故障：

```text
发送成功
↓
结果返回丢失
↓
Agent 认为失败
↓
重试
↓
重复发送
```

单纯有 Checkpoint 解决不了。

需要：

```text
operation_id
+
payload hash
+
业务服务幂等
+
结果对账
```

---

### 4. Memory 必须有来源和版本

Memory 不应该只是：

```json
{
  "budget": 5000
}
```

更合理的是：

```json
{
  "value": 5000,
  "source": "user",
  "revision": 3,
  "observed_at": "...",
  "expires_at": null
}
```

这样才能解决：

- 用户纠正；
- 旧消息迟到；
- 权威数据冲突；
- 删除；
- 过期。

---

### 5. Agent 的成功必须由外部结果判断

Agent 说：

> “已经完成任务。”

不代表真的完成。

例如 Coding Agent 应该检查：

```text
代码是否修改
测试是否通过
是否修改无关文件
最终 git diff
```

业务 Agent 应该检查：

```text
数据库状态
实际工具调用
消息是否重复
审批是否有效
状态版本是否正确
```

---

## 对我们最值得做的 3 个 PoC

### PoC 1：Memory

研究：

- 滑动窗口；
- 摘要；
- 结构化 Memory；
- RAG；
- 来源；
- TTL；
- 删除；
- 冲突处理。

重点指标不是“记住多少”，而是：

> **关键事实是否正确。**

---

### PoC 2：异步 Agent + 状态机

针对：

```text
一轮对话结束
→ Agent 异步生成结果
→ 用户已经进入下一轮
```

重点解决：

- stale result；
- 重复任务；
- 乱序；
- 状态版本；
- 合法阶段流转。

建议采用：

```text
turn_id
state_version
event_id
CAS
```

---

### PoC 3：大规模 Agent 执行

重点不是模型，而是：

- 分片；
- 队列；
- 限流；
- 幂等；
- 重试；
- DLQ；
- 对账；
- 发送前二次检查。

Agent 作为生成 / 决策节点嵌入传统异步系统，而不是替代传统后端。

---

## 当前建议

### 短期

不要进行“大框架迁移”。

先做一层稳定接口：

```text
Agent
 ↓
Tool Gateway
 ↓
Auth / Idempotency / State Validation
 ↓
Business Service
```

这样未来换：

- OpenAI
- Claude
- LangGraph
- ADK

业务安全逻辑都不需要重写。

### 中期

选择两个方向做真实对照：

**明确业务流程：**

> LangGraph / ADK / Microsoft Agent Framework

**开放式长任务：**

> Claude Agent SDK / Deep Agents

同时保留最小单 Agent 方案作为 baseline。

### 长期

形成自己的：

> **Agent Runtime + Business Control Plane**

真正形成壁垒的不是“用了哪个框架”，而是：

- Memory 管理；
- 状态管理；
- Tool Gateway；
- 权限；
- 幂等；
- Evaluation；
- Observability；
- 成本控制。

---

## 这次研究目前做到什么程度

已经完成：

- 31 项官方/上游资料核验；
- 6 个核心技术体系；
- 6 款产品研究卡；
- 4 个补充项目；
- 2 处局部源码核验；
- 30 项原创离线工程实验；
- 35 个真实模型评测任务设计。

尚未完成：

- 真实模型 420 次横向运行；
- 商业产品原生任务实测；
- 生产级压力测试；
- 安全审计。

因此：

> **现在可以用于架构讨论、技术路线选择和 PoC 设计，但还不能用于宣布“某框架性能第一”。**

---

## 最终结论

如果只记住一句：

> **未来 Agent 系统的核心不是“模型自己做所有事情”，而是让模型负责理解和决策，让框架负责执行过程，让传统业务系统继续掌握权限、事实和最终写入。**

这也是这个调研项目最值得继续深入的主线。
