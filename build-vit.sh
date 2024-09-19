tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-vit:latest -f Dockerfile-VIT .
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-vit:latest
docker tag registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-vit:latest registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-vit:$tag
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-vit:$tag