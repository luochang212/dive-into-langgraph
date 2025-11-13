"""
基于阿里百炼平台 API 的 RAG 示例

参考: https://docs.langchain.com/oss/python/langchain/rag#build-a-rag-agent-with-langchain
"""

import os
import bs4

from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 加载模型配置
_ = load_dotenv()


# 加载模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3-coder-plus",
    temperature=0.7,
)

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

# DashScope 兼容的 OpenAIEmbeddings 实现
class DashScopeEmbeddings(Embeddings):
    def __init__(self, model: str = "text-embedding-v4", dimensions: int = 1024):
        self.model = model
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), 10):
            chunk = texts[i : i + 10]
            r = client.embeddings.create(
                model=self.model,
                input=chunk,
                dimensions=self.dimensions,
            )
            out.extend([d.embedding for d in r.data])
        return out

    def embed_query(self, text: str) -> list[float]:
        r = client.embeddings.create(
            model=self.model,
            input=[text],
            dimensions=self.dimensions,
        )
        return r.data[0].embedding

# 初始化内存向量存储
embeddings = DashScopeEmbeddings()
vector_store = InMemoryVectorStore(embedding=embeddings)

# Only keep post title, headers, and content from the full HTML.
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://luochang212.github.io/posts/quick_bi_intro/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()

assert len(docs) == 1
# print(f"Total characters: {len(docs[0].page_content)}")
# print(docs[0].page_content[:500])

# 文本分块
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)

# print(f"Split blog post into {len(all_splits)} sub-documents.")

# 将文档添加到向量存储
document_ids = vector_store.add_documents(documents=all_splits)

# print(document_ids[:3])

# 创建上下文检索工具
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# 创建 ReAct Agent
agent = create_agent(
    llm,
    tools=[retrieve_context],
    system_prompt=(
        # If desired, specify custom instructions
        "You have access to a tool that retrieves context from a blog post. "
        "Use the tool to help answer user queries."
    )
)

# 测试 ReAct Agent
query = "当前的 Agent 能力，有哪些局限？"

for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
