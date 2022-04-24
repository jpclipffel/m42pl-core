cd $(dirname $0)
docker buildx build \
    -t m42pl:latest \
    -t jpclipffel/m42pl:latest \
    -f ./Dockerfile \
    ../../../
