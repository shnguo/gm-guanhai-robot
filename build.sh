tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest .
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest
docker tag gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:$tag
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:$tag

docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest
docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:$tag