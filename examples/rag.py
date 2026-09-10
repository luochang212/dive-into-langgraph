"""
基于阿里百炼平台 API 的 RAG 示例

参考: https://docs.langchain.com/oss/python/langchain/rag#build-a-rag-agent-with-langchain
"""

import os

import bs4
import requests

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 加载模型配置
load_dotenv()


# 加载模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3.7-flash",
    temperature=0.7,
)


# 初始化内存向量存储（DashScope 兼容 OpenAI 的 Embeddings 接口）
embeddings = OpenAIEmbeddings(
    model="text-embedding-v4",
    dimensions=1024,
    check_embedding_ctx_length=False,  # 关闭本地 token 切分，直接提交原文
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)
vector_store = InMemoryVectorStore(embedding=embeddings)


def load_web_page(url: str, strainer: bs4.SoupStrainer | None = None) -> list[Document]:
    """抓取网页并提取正文"""
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        },
        timeout=30,
    )
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, "html.parser", parse_only=strainer)
    return [Document(page_content=soup.get_text(), metadata={"source": url})]


bs4_strainer = bs4.SoupStrainer(class_=("post"))
docs = load_web_page("https://luochang212.github.io/posts/quick_bi_intro/", bs4_strainer)

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
        (f"Source: {doc.metadata}\nContent: {doc.page_content}") for doc in retrieved_docs
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
    ),
)

# 测试 ReAct Agent
query = "当前的 Agent 能力，有哪些局限？"

for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
