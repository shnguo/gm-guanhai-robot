FROM --platform=linux/amd64  docker.io/bitnami/python:latest
# RUN apt update \
#     && DEBIAN_FRONTEND=noninteractive apt install -y tzdata \
#     && rm -rf /var/lib/apt/lists/*

# 设置默认时区
ENV TZ=Asia/Shanghai
WORKDIR /workspace

# COPY ./mbart-large-50-many-to-one-mmt ./mbart-large-50-many-to-one-mmt
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY ./utils /workspace/utils
COPY ./server.py /workspace/

CMD ["python", "server.py"]