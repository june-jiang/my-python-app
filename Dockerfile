# 1. 使用官方轻量级 Python 基础镜像
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖清单并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制应用代码
COPY app.py .

# 5. 暴露 5000 端口并启动应用
EXPOSE 5000
CMD ["python", "app.py"]