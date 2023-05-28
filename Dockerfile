FROM python:alpine

ARG BUILD_VERSION="1.0.0-snapshot"
ARG PROJECT_NAME=
ARG BUILD_SHA=
ARG BUILD_DATE=
ARG BUILD_REF=

ENV APP_VERSION=${BUILD_VERSION}
ENV APP_BUILD_DATE=${BUILD_DATE}
ENV APP_BUILD_REF=${BUILD_REF}
ENV APP_BUILD_SHA=${BUILD_SHA}


ENV DELUGE_HOST="localhost"
ENV METRICS_PORT="9354"

LABEL VERSION="${BUILD_VERSION}"
LABEL PROJECT_NAME="${PROJECT_NAME}"

COPY app/ /app

RUN pip install -r /app/setup/requirements.txt

RUN rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -rf /app/setup

EXPOSE 9354
ENTRYPOINT ["/usr/local/bin/python", "/app/deluge_exporter.py"]
