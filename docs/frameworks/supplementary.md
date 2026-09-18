# 补充观察：CrewAI、LlamaIndex、Dify、Coze Studio

范围说明：本轮为文档级定位研究，不纳入“已测SDK”或商业产品性能比较。

## CrewAI

D｜官方文档将可编程Flows与以Agents协作组织的Crews组合起来。[S24]

I｜适合用来检查“外层确定性控制＋内层自主协作”的设计。不要从角色分工名称推导真实并行度或高可靠性。候选实验应同时保留单Agent版本，比较任务依赖较强时是否出现重复检索、循环委派和整合失败。当前未安装，因此不比较具体API或迁移难度。

## LlamaIndex

D｜官方Agent文档展示FunctionAgent、查询引擎工具封装及AgentWorkflow，支持将检索接口加入工具执行循环。[S25]

I｜适合从数据/检索质量切入。应把“找到了正确证据”和“正确执行了工作流”分开评分：索引、重排和引用改善可能来自检索组件，而不是多Agent协调。对于有大量知识库的场景，先固定知识切片和查询工具再比较编排，避免用不同数据管线制造不可比结果。

## Dify

D｜官方Workflow Studio说明包括可视化节点、知识检索、代码、工具、分支和人工输入，以及应用/API发布方式。[S26]

I｜价值主要体现在团队配置、交付与运维控制面，不应与SDK代码行数直接对比。需要额外检查配置版本、审批变更、调试数据、插件身份与上线回滚。首轮适合用一条可见业务流验证从编辑、测试到发布的闭环，而不是只截取画布截图。

## Coze Studio

D｜上游README展示Agent/App/Workflow、资源与API范围，并说明开源/商业功能存在差异；后端使用Go。README明确提醒公开网络部署时的账号、代码执行、SSRF和接口权限风险。[S27]

I｜评估对象必须写“Coze Studio开源版本＋具体commit/镜像”，不能用云产品宣传替代自部署能力。鉴于其公开部署提醒，实验应在隔离网络使用合成数据，不能为了试用直接暴露管理入口。

## 补充对象的统一门槛

能导出可审阅配置、能记录执行终态、能限制工具身份、能找出失败路径、能明确版本。未达到某门槛时先记录缺口；未测试不记作“不支持”。


## 证据来源

- [S24] [CrewAI introduction](https://docs.crewai.com/v1.15.14/en/introduction/index.html)。检索入口重定向文档v1.15.14；不等于最新安装包。
- [S25] [LlamaIndex Agents](https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/)。滚动文档；读取Agent/Tools/Multi-Agent章节。
- [S26] [Dify Workflow Studio](https://www.dify.ai/workflows)。官方产品说明；未部署。
- [S27] [Coze Studio README](https://github.com/coze-dev/coze-studio/blob/main/README.md)。blob 6f4221d806888d45596156bec6f5599294ea6a2f；读取1–140行。
