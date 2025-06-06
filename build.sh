#!/bin/bash
# Build script for Skyhigh Traffic Forge Docker image

set -e

echo "Skyhigh Traffic Forge - Docker Build Script"
echo "============================================="
echo

# Default values
IMAGE_NAME="${IMAGE_NAME:-skyhigh-traffic-forge}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"

# Read version from VERSION file
if [ -f VERSION ]; then
    VERSION=$(cat VERSION)
    echo "Building version: ${VERSION}"
    # Use version as tag if no tag specified
    if [ "${IMAGE_TAG}" = "latest" ]; then
        IMAGE_TAG="${VERSION}"
    fi
fi

# Get build metadata
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Build the image
echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
docker build \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg VCS_REF="${VCS_REF}" \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -t "${IMAGE_NAME}:latest" \
    .

# Tag with registry if provided
if [ -n "${REGISTRY}" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "Tagging image as: ${FULL_IMAGE}"
    docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE}"
    
    echo
    echo "To push to registry:"
    echo "  docker push ${FULL_IMAGE}"
fi

echo
echo "Build complete!"
echo
echo "To test the image:"
echo "  mkdir -p test-config"
echo "  docker run -v \$(pwd)/test-config:/etc/shadow-it-generator ${IMAGE_NAME}:${IMAGE_TAG} init"
echo "  docker run -v \$(pwd)/test-config:/etc/shadow-it-generator ${IMAGE_NAME}:${IMAGE_TAG} generate --mode realtime --display console"
echo

# Show image size
echo "Image info:"
docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"