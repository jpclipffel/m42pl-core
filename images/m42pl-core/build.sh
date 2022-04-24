cd $(dirname $0)
docker buildx build \
    -t m42pl-core:latest \
    -t jpclipffel/m42pl-core:latest
    -f ./Dockerfile \
    ../../
