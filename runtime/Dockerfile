FROM python:3.12-alpine

COPY entrypoint.py /usr/local/bin/atlas-runtime
RUN chmod +x /usr/local/bin/atlas-runtime

ENTRYPOINT ["/usr/local/bin/atlas-runtime"]
