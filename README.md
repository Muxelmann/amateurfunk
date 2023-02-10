# Amateurfunk

Mit diesem Webserver kann man sich auf die deutsche Amateurfunkprüfung vorbereiten.

Auch verfügbar auf [docker hub](https://hub.docker.com/repository/docker/muxelmann/amateurfunk/).

## Building

```sh
docker buildx build \
    --push \
    --platform linux/arm64/v8,linux/arm/v7,linux/amd64 \
    --tag muxelmann/amateurfunk \
    .
```

## Running

```sh
docker run \
    -v /path/to/instance:/code/instance:rw \
    -e FLASK_SECRET=<SOME_SECRET_FOR_COOKIE_CACHE> \
    -p 8080:80/tcp
    muxelmann/amateurfunk
```