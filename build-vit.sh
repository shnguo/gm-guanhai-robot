tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest -f Dockerfile-VIT .
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest
docker tag gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag
docker push gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag

docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest
docker rmi gm-guanhai-registry.cn-shanghai.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag