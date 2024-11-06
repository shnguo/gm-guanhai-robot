tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:latest -f Dockerfile-VLLM .
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:latest
docker tag gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:latest gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:$tag
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:$tag

docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:latest
docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vllm:$tag