# OpenAI Agents SDK：轻量执行循环，不替代业务事务

**研究对象：Python SDK；D+局部S；未运行SDK或调用模型。** 安装版本未冻结，下面不是对任意历史版本的保证。

## 已确认的设计

D｜Agent、Runner、工具与handoff构成核心抽象；SDK负责多步模型/工具交互，而不是只包装一次请求。[S01]

D｜Session保存多轮历史；同一次run中不能把session与conversation_id/previous_response_id等服务端延续选项叠加。审批恢复需要使用相同会话及后端；历史筛选接口控制输入，不等于重新写入旧历史。[S03]

D/S｜输入Guardrail默认并行运行。源码`InputGuardrail.run_in_parallel=True`与文档一致。文档区分输入首Agent、输出末Agent和FunctionTool调用检查，不能理解为每一种工具都受同一个安全链保护。[S02][S05]

D｜默认追踪覆盖模型、工具、handoff等；敏感数据采集有独立配置，自定义处理器可以改变导出目的地。[S04]

## 架构解释（I）

建议将SDK放在“模型编排与工具适配层”，将身份、授权、审批记录、订单状态和操作幂等放在应用/业务服务层。handoff表示执行控制权的转移，不能被等同于独立部署的Agent服务之间已经具备事务一致性。

```text
用户请求 → 身份/业务前置校验 → Runner
                              ├─ 模型 → FunctionTool → 业务授权网关
                              ├─ handoff → 专用Agent
                              └─ Session / Trace
业务授权网关 → 带幂等键的业务服务 → 权威结果
```

## 一个必须注意的失败窗口（I）

当输入检查和Agent并行时，慢检查可能在写工具之后才判定拒绝。抛出异常能够停止后续步骤，却无法自动撤销已经提交的业务动作。因此，高风险写入需要执行点的独立授权，不能仅依赖开头的文本过滤。选择串行输入检查可以缩小窗口，但仍不能替代后端授权、参数验证和幂等。

类似地，Session成功恢复说明能找回历史，不证明一个返回丢失的外部API没有执行。操作ID必须跨重试保持一致，并由接收方原子去重。

## 适用与不适用的判断（I）

适合作为工具型服务与模型循环的候选基线，尤其当团队希望少量抽象、自己掌控业务控制面时。复杂的确定性SOP、跨进程作业调度、补偿与审计需要明确配置/外部实现；不因SDK包含guardrails和sessions就认定全部可靠性工作已完成。

已有业务平台可以只接入模型循环与追踪，而不让SDK成为业务状态唯一存储。多供应商对照还需核验模型适配器行为，不能只改model字符串便认为条件相同。

## 首轮可验证问题

|检查|判断标准|
|---|---|
|并行与串行输入检查|写动作是否发生在拒绝之前；时延单独记录|
|FunctionTool和托管/内置工具|逐类核验检查点，记录未覆盖路径|
|审批暂停/重启|恢复相同session且不得绕过已拒绝审批|
|历史压缩/筛选|关键事实与最新纠正保留，不误写旧消息|
|日志出口|验证敏感字段脱敏、采集开关和实际导出目标|

本包的权限顺序和幂等实验只验证原创机制，**不证明SDK上述用例已通过**。


## 证据来源

- [S01] [OpenAI Agents SDK overview](https://openai.github.io/openai-agents-python/)。滚动文档；未锁定安装包版本。
- [S02] [OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)。滚动文档。
- [S03] [OpenAI Sessions](https://openai.github.io/openai-agents-python/sessions/)。滚动文档。
- [S04] [OpenAI Tracing](https://openai.github.io/openai-agents-python/tracing/)。滚动文档。
- [S05] [OpenAI guardrail.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/guardrail.py)。blob 07475c8183835ae42d9242bcf0f1bcdb93732ed6；阅读1–220行。
