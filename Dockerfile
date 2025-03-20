# Alpine 无法支持使用系统的docker
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["bash", "start-server.sh"]