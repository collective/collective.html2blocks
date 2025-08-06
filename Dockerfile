# syntax=docker/dockerfile:1.9
FROM ubuntu:noble AS base

ARG PYTHON_VERSION=3.12
ARG PB_VERSION

SHELL ["sh", "-exc"]
ENV DEBIAN_FRONTEND=noninteractive
RUN <<EOT
    buildDeps="build-essential busybox ca-certificates curl git gosu libbz2-dev libffi-dev libjpeg-turbo8-dev libmagic1 libsasl2-dev libldap2-dev libopenjp2-7-dev libpcre3-dev libpq-dev libssl-dev libtiff6 libtiff5-dev libxml2-dev libxslt1-dev python3-setuptools python$PYTHON_VERSION-dev wget zlib1g-dev"
    apt-get update -qy
    apt-get install -qyy \
        -o APT::Install-Recommends=false \
        -o APT::Install-Suggests=false \
        $buildDeps
    busybox --install -s
EOT

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python$PYTHON_VERSION \
    UV_PROJECT_ENVIRONMENT=/app


RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-group test \
        --no-install-project

COPY . /src
WORKDIR /src

# Install package
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
        --locked \
        --no-dev \
        --no-group test \
        --no-editable

FROM ubuntu:noble

ARG PYTHON_VERSION=3.12

SHELL ["sh", "-exc"]
RUN <<EOT
    set -e
    useradd --system -m -d /app -U -u 500 plone
    runDeps="ca-certificates git libjpeg8 libopenjp2-7 libpq5 libtiff6 libxml2 libxslt1.1 lynx netcat-openbsd python3-setuptools python$PYTHON_VERSION-dev poppler-utils rsync wv busybox gosu libmagic1 make"
    apt-get update
    apt-get -y upgrade
    apt-get install -y --no-install-recommends $runDeps
    apt-get clean -y
    busybox --install -s
    rm -rf /var/lib/apt/lists/* /usr/share/doc
EOT

LABEL maintainer="Plone Collective <collective@plone.org>" \
      org.label-schema.name="ghcr.io/collective/html2blocks" \
      org.label-schema.description="Convert html to Volto blocks." \
      org.label-schema.vendor="Plone Collective"

EXPOSE 8000

# Copy the pre-built `/app` directory to the runtime container
# and change the ownership to user app and group app in one step.
COPY --from=base --chown=500:500 /app /app

# Set healthcheck to port 8080
HEALTHCHECK --interval=5s --timeout=2s --start-period=20s CMD [ -n "$LISTEN_PORT" ] || LISTEN_PORT=8000 ; wget -q http://127.0.0.1:"$LISTEN_PORT"/ok -O - | grep OK || exit 1

ENTRYPOINT [ "/app/bin/html2blocks" ]
CMD ["server", "--host", "0.0.0.0"]
