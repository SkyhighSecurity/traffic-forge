# Skyhigh Traffic Forge - Docker Image
# Generates realistic web gateway traffic logs for CASB demonstrations

FROM python:3.11 AS builder

# Copy VERSION file to read the version
COPY VERSION /VERSION

# Export version for use in final stage
RUN echo "APP_VERSION=$(cat /VERSION)" > /version.env

FROM python:3.11

# Copy version info from builder
COPY --from=builder /version.env /version.env
COPY VERSION /app/VERSION

# Source version and display it
RUN . /version.env && \
    echo "Building Skyhigh Traffic Forge version: $APP_VERSION"

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF

# Set version as environment variable for runtime
ENV APP_VERSION_FILE=/app/VERSION

LABEL maintainer="Skyhigh Security"
LABEL description="Skyhigh Traffic Forge - Web Gateway Traffic Simulator for CASB Demos"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.title="Skyhigh Traffic Forge"
LABEL org.opencontainers.image.description="Web Gateway Traffic Simulator for CASB Demos"
LABEL org.opencontainers.image.vendor="Skyhigh Security"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 skyhigh && \
    mkdir -p /etc/skyhigh-traffic-forge \
             /var/log/skyhigh-traffic-forge \
             /usr/share/skyhigh-traffic-forge/data \
             /app && \
    chown -R skyhigh:skyhigh /etc/skyhigh-traffic-forge \
                              /var/log/skyhigh-traffic-forge \
                              /app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY setup.py .
COPY README.md .
COPY VERSION .

# Install the package
RUN pip install --no-cache-dir -e .

# Copy template configs to system location
RUN cp -r config/* /usr/share/skyhigh-traffic-forge/ && \
    cp -r data/* /usr/share/skyhigh-traffic-forge/data/

# Switch to non-root user
USER skyhigh

# Configuration volume - users should mount their config here
VOLUME ["/etc/skyhigh-traffic-forge"]

# Output volume - logs will be written here
VOLUME ["/var/log/skyhigh-traffic-forge"]

# Default environment variables
ENV SKYHIGH_CONFIG_DIR=/etc/skyhigh-traffic-forge
ENV SKYHIGH_OUTPUT_DIR=/var/log/skyhigh-traffic-forge
ENV SKYHIGH_LOG_LEVEL=INFO

# Entrypoint script to handle initialization
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default command
CMD ["generate", "--mode", "realtime"]