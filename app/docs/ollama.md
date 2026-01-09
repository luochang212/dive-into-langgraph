## 使用 Ollama 本地部署 `qwen3:4b`

下面以 macOS 为例，其他桌面系统步骤类似。

### 1. 安装 Ollama

- **访问官网**: `https://ollama.com`
- **下载并安装** 对应系统的安装包（macOS/Windows/Linux）
- 安装完成后，终端中可以使用 `ollama` 命令

### 2. 下载 `qwen3:4b` 模型

在终端执行：

```bash
ollama pull qwen3:4b
```

等待模型下载完成。

### 3. 启动 Ollama 服务

#### 3.1 只在本机使用

```bash
ollama serve
```

默认会在 `http://127.0.0.1:11434` 暴露 HTTP 接口。

#### 3.2 局域网访问（可被其他机器 / Docker 调用）

```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

然后在别的机器上，用你这台机器的 IP 和端口 `11435` 即可访问。

### 4. 简单测试接口

```bash
curl http://127.0.0.1:11435/api/generate -d '{
  "model": "qwen3:4b",
  "prompt": "用一句话介绍一下你自己。"
}'
```

看到有流式返回内容，说明本地 qwen3:4b + Ollama 服务已经正常工作。

### 5. 在 LangChain 中使用

```python
"""
运行方法：
    pip install -U langchain-openai
    OLLAMA_HOST=0.0.0.0:11435 ollama serve
    python ollama.py
"""

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen3:4b",
    base_url="http://127.0.0.1:11435/v1",
    api_key="-",
)

resp = llm.invoke("用一句话介绍一下你自己。")
print(resp.content)

# for chunk in llm.stream("用一句话介绍一下你自己。"):
#     print(chunk.content, end="", flush=True)
```
