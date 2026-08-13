FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod go.sum* ./
COPY main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' -o /out/atlas-runtime .

FROM alpine:3.22
COPY --from=build /out/atlas-runtime /usr/local/bin/atlas-runtime
ENTRYPOINT ["/usr/local/bin/atlas-runtime"]
