ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.21
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apk add --no-cache \
    curl \
    build-base \
    linux-headers \
    python3 \
    python3-dev \
    py3-pip

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Copy application code
COPY rootfs /

# Make scripts executable
RUN chmod a+x /usr/bin/run.sh && \
    chmod a+x /usr/share/casabot/health_check.py

# Set workdir
WORKDIR /usr/share/casabot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 /usr/share/casabot/health_check.py

# Start script
CMD ["/usr/bin/run.sh"]