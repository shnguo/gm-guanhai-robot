tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-robot:latest .
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-robot:latest
docker tag registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-robot:latest registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-robot:$tag
docker push registry.cn-shanghai.aliyuncs.com/vevor_devops/gm-guanhai-robot:$tag