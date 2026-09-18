# 局部源码核验记录

## S05：OpenAI InputGuardrail

路径：`src/agents/guardrail.py`，读取1–220行。实际返回blob：`07475c8183835ae42d9242bcf0f1bcdb93732ed6`。

观察：InputGuardrail有`run_in_parallel`字段，默认True；结果封装含tripwire字段，执行函数允许同步或异步返回。此局部阅读与Guardrails文档的默认并行说明相互印证。

限制：没有读取整个Runner调度实现、所有工具类别的执行路径或其测试，也没有运行SDK。因此“延后拒绝无法撤销外部副作用”是工程推论，原创实验只展示该类反例，不冒充SDK故障复现。

## S09：LangGraph InMemorySaver

路径：`libs/checkpoint/langgraph/checkpoint/memory/__init__.py`，读取1–130行。实际返回blob：`0f0719c61fe64efddd0e1837eefd94eff23d39f9`。

观察：默认factory为defaultdict，构造器创建storage、writes、blobs；源码说明默认内存实现用于调试/测试。非默认factory有不同管理逻辑，本报告不将其一概判为纯内存。

限制：没有读取完整持久化生态、PostgreSQL后端或恢复调度器。未执行此实现，不对跨进程恢复效果报分。

## 引用稳定性

GitHub页面URL使用main，会变化；blob SHA标识本次返回内容。blob SHA不是commit SHA，不能把它拼成`blob/<commit>/path`冒充固定提交。可通过上游Git blobs接口核对：

- [OpenAI blob](https://api.github.com/repos/openai/openai-agents-python/git/blobs/07475c8183835ae42d9242bcf0f1bcdb93732ed6)
- [LangGraph blob](https://api.github.com/repos/langchain-ai/langgraph/git/blobs/0f0719c61fe64efddd0e1837eefd94eff23d39f9)

DeepSeek读取的是架构文档，不将其记为完整源码审计；Coze读取README，也只记为文档证据。


## 证据来源

- [S05] [OpenAI guardrail.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/guardrail.py)。blob 07475c8183835ae42d9242bcf0f1bcdb93732ed6；阅读1–220行。
- [S09] [LangGraph InMemorySaver implementation](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/memory/__init__.py)。blob 0f0719c61fe64efddd0e1837eefd94eff23d39f9；阅读1–130行。
- [S02] [OpenAI Guardrails](https://openai.github.io/openai-agents-python/guardrails/)。滚动文档。
