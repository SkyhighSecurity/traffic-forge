#!/bin/bash
# Standalone initialization script for Skyhigh Traffic Forge

set -e

echo "======================================"
echo "Skyhigh Traffic Forge - Initialize"
echo "======================================"
echo ""

# Create required directories
echo "Creating required directories..."
mkdir -p ./config ./logs

# Run initialization using Docker directly
echo "Initializing configuration..."
docker run --rm \
  -v $(pwd)/config:/etc/skyhigh-traffic-forge \
  -u "${UID:-1000}:${GID:-1000}" \
  ghcr.io/skyhighsecurity/traffic-forge:latest init

# Check if initialization was successful
if [ -f ./config/enterprise.yaml ]; then
    echo ""
    echo "✓ Configuration initialized successfully!"
    echo ""
    echo "Configuration files created in ./config/"
    echo ""
    echo "Next steps:"
    echo "1. Edit ./config/enterprise.yaml to match your organization"
    echo "2. Start the traffic generator with: docker compose up -d"
    echo "3. View logs with: docker compose logs -f"
    echo ""
else
    echo ""
    echo "✗ Configuration initialization failed!"
    echo ""
    echo "Please check Docker is running and you have internet connectivity."
    exit 1
fi