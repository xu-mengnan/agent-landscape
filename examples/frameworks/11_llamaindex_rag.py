# /// script
# requires-python = ">=3.11"
# dependencies = ["llama-index-core", "llama-index-llms-openai", "llama-index-embeddings-openai"]
# ///
"""LlamaIndex：小文档库 → 向量索引 → 查询工具 → Agent 回答。
看点：把数据检索管线包装成 QueryEngineTool，而不把全部文档硬塞进提示词。
Embedding 与回答都会调用 API；资料是虚构办公手册，不是现实制度。
"""
from _common import env, launch


async def run(_):
    from llama_index.core import Document, VectorStoreIndex
    from llama_index.core.tools import QueryEngineTool
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding

    llm = OpenAI(model=env("OPENAI_MODEL"), timeout=40, max_retries=0)
    embedding = OpenAIEmbedding(model=env("OPENAI_EMBEDDING_MODEL"), timeout=40, max_retries=0)
    documents = [
        Document(text="虚构手册：投影仪故障请先重启，再联系设备管理员小林。",
                 metadata={"source": "equipment-guide"}),
        Document(text="虚构手册：会议室可提前7天预订，会议结束请清理白板。",
                 metadata={"source": "room-guide"}),
    ]
    index = VectorStoreIndex.from_documents(documents, embed_model=embedding)
    engine = index.as_query_engine(llm=llm, similarity_top_k=1)
    tool = QueryEngineTool.from_defaults(
        query_engine=engine, name="office_handbook",
        description="查询虚构办公手册，包括设备故障处理和会议室预订。",
    )
    agent = FunctionAgent(tools=[tool], llm=llm,
                          system_prompt="办公制度问题必须先查询 office_handbook；没有证据就说明不知道。")
    result = await agent.run(user_msg="投影仪坏了应该先做什么，再找谁？")
    print("[索引文档数]", len(documents))
    print("[Agent 回答]", result)
    print("[工具] office_handbook；回答须与虚构手册核对，不能只看语言流畅。")


if __name__ == "__main__":
    launch(run, __doc__, ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_EMBEDDING_MODEL"))
