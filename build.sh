tag=$(date '+%Y-%m-%d-%H-%M-%S')
docker buildx build --platform linux/amd64 -t crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest .
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest
docker tag crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:latest crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:$tag
docker push crpi-67yitwjy0o6k9icc.cn-hangzhou.personal.cr.aliyuncs.com/gm-aigc/gm-guanhai-robot:$tag