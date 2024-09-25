tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-aigc:latest -f Dockerfile-AIGC . 
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-aigc:latest
docker tag registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-aigc:latest registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-aigc:$tag
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-aigc:$tag