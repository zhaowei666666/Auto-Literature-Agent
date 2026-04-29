# 使用轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (pdfplumber 及其底层依赖)
RUN apt-get update && apt-get install -is-quiet --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir python-dotenv

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p pdfs outputs

# 设置环境变量默认值
ENV PYTHONUNBUFFERED=1

# 启动命令
ENTRYPOINT ["python", "main.py"]
