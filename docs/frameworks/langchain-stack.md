# LangChain / LangGraph / Deep Agents：按责任层选，而非互相替代

**D+局部S；未安装运行。** 对比的是不同层次，不给三个名称放同一总分。

## 已确认的职责

D｜LangChain提供较高层Agent/模型/工具抽象，LangGraph定位在编排运行时；Deep Agents是带上下文与工具设施的Harness。LangGraph并不要求应用必须同时使用LangChain。[S06]

D｜LangGraph将线程执行状态的checkpointer与应用自定义跨线程store分开；持久性取决于存储后端，内存方式不能承诺重启恢复。[S07]

S｜读取`InMemorySaver`前130行，看到默认存储通过`defaultdict`创建；源码明确其调试/测试用途。这个事实不是对全部checkpointer的否定。[S09]

D｜Deep Agents整合文件系统、上下文压缩/卸载和隔离子Agent上下文；当前文档把planning、Skills等列为可配置能力，不能将所有模块都说成无条件默认启用。[S08]

## 应用责任与运行时责任（I）

建议让运行时承载“接下来执行哪一步、如何保存执行进度”；让业务状态服务承载“事实是什么、谁能修改、哪个版本仍有效”。线程ID不是天然的租户授权边界；store namespace也不能替代访问控制。

图节点可执行确定性函数，也可调用模型。业务SOP需要明确前置边和校验节点，开放生成可以局部保留循环。把所有分支交给LLM决定与把所有内容固定为DAG是两个极端；需要根据业务动作风险划界。图也可以有循环，不应把LangGraph笼统说成只能DAG。

## 上下文设计（I）

建议分离：最近对话、经过校验的业务状态、带来源和时效的长期事实、按任务检索的证据。即使压缩组件自动节省上下文，也应测试信息纠正、来源冲突、删除和审批状态，而不仅比较Token。

子Agent适合隔离大量中间探索过程。父Agent应接收小而有来源的结果契约，不必接收全部工具输出。并行任务必须定义结果冲突仲裁者与成本上限，否则只是把一个长上下文变成多个收费上下文。

## 失败模式与验证重点

|边界|容易误判|需要的验证|
|---|---|---|
|检查点|能恢复即不会重复动作|返回丢失后重放与接收方幂等|
|内存后端|开发Demo即持久化方案|真实进程退出后恢复|
|store|跨线程记忆自动正确|租户、字段权威、TTL及删除传播|
|子图|共享字段天然无冲突|并行更新/reducer/版本冲突|
|文件卸载|移出prompt就无损|检索回读、过期文件和授权|
|升级|代码可启动即能恢复旧任务|旧检查点+新拓扑/序列化兼容测试|

## 采用判断（I）

对于需要明确状态转移、人工暂停、失败定位的业务，可优先将LangGraph列入受控验证。任务以开放研究、文件操作和较长上下文为主时，Deep Agents值得单独验证。简单工具循环不应为了“多Agent架构”强行引入复杂图。

这是需求匹配判断，不是本项目证明LangGraph性能最优。正式采用前仍需要持久后端、幂等网关、版本迁移、权限和运行成本评估。


## 证据来源

- [S06] [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)。滚动文档。
- [S07] [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。滚动文档；durable-execution入口重定向至此。
- [S08] [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)。滚动文档。
- [S09] [LangGraph InMemorySaver implementation](https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/memory/__init__.py)。blob 0f0719c61fe64efddd0e1837eefd94eff23d39f9；阅读1–130行。
