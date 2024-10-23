FROM --platform=linux/amd64  registry.cn-shanghai.aliyuncs.com/shnguo/pytorch.pytorch:2.4.0-cuda12.4-cudnn9-devel
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt install -y tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置默认时区
ENV TZ=Asia/Shanghai
WORKDIR /workspace

# COPY ./mbart-large-50-many-to-one-mmt ./mbart-large-50-many-to-one-mmt
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY ./utils /workspace/utils
COPY ./dependencies /workspace/dependencies
COPY ./server.py /workspace/

CMD ["uvicorn", "server:app","--host","0.0.0.0","--port","8004"]