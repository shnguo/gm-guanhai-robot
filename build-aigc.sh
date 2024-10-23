tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest -f Dockerfile-AIGC . 
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest
docker tag gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag

docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest
docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag