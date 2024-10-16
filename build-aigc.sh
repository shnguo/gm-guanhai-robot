tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest -f Dockerfile-AIGC . 
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest
docker tag crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag

docker rmi crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:latest
docker rmi crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-aigc:$tag