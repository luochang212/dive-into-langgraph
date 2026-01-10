FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 更换为国内镜像源并安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python依赖
COPY pyproject.toml .
RUN pip install uv==0.9.24 -i https://mirrors.aliyun.com/pypi/simple/
RUN uv sync -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY app.py .
COPY .env .
COPY images/ ./images/
COPY mcp/ ./mcp/
COPY prompts/ ./prompts/
COPY space/ ./space/
COPY tools/ ./tools/
COPY utils/ ./utils/

# 复制supervisor配置文件
COPY docker.conf /etc/supervisor/conf.d/supervisord.conf

# 设置入口点
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
