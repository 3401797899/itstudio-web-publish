# 使用Alpine作为基础镜像
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]