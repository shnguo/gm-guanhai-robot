tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest -f Dockerfile-VIT .
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest
docker tag crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag

docker rmi crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:latest
docker rmi crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-vit:$tag