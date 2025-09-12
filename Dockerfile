ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:3.11-alpine3.18
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apk add --no-cache \
    curl \
    build-base \
    linux-headers

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY rootfs /

# Make script executable
RUN chmod a+x /usr/bin/run.sh

# Set workdir
WORKDIR /usr/share/casabot

# Start script
CMD ["/usr/bin/run.sh"]