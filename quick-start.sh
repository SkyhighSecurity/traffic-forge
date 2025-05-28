#!/bin/bash
# Quick start script for Skyhigh Traffic Forge

set -e

echo "======================================"
echo "Skyhigh Traffic Forge - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed or not available."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Function to display usage
usage() {
    echo "Usage: $0 [init|start|stop|logs|status|clean]"
    echo ""
    echo "Commands:"
    echo "  init    - Initialize configuration (first time setup)"
    echo "  start   - Start generating traffic logs"
    echo "  stop    - Stop traffic generation"
    echo "  logs    - View generator logs"
    echo "  status  - Check generator status"
    echo "  clean   - Remove all generated logs (caution!)"
    echo ""
    exit 1
}

# Function to initialize configuration
init_config() {
    echo "Initializing configuration..."
    
    # Create config directory if it doesn't exist
    mkdir -p ./config
    
    # Run init using docker compose
    docker compose -f docker-compose.init.yml up
    
    if [ -f ./config/enterprise.yaml ]; then
        echo ""
        echo "✓ Configuration initialized successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Edit ./config/enterprise.yaml to match your organization"
        echo "2. Run '$0 start' to begin generating logs"
        echo ""
    else
        echo "✗ Configuration initialization failed!"
        exit 1
    fi
}

# Function to start traffic generation
start_generator() {
    if [ ! -f ./config/enterprise.yaml ]; then
        echo "Error: Configuration not found. Run '$0 init' first."
        exit 1
    fi
    
    echo "Starting traffic generator..."
    docker compose up -d
    
    echo ""
    echo "✓ Traffic generator started!"
    echo ""
    echo "View logs with: $0 logs"
    echo "Check status with: $0 status"
    echo ""
}

# Function to stop traffic generation
stop_generator() {
    echo "Stopping traffic generator..."
    docker compose down
    echo "✓ Traffic generator stopped!"
}

# Function to view logs
view_logs() {
    docker compose logs -f --tail=100
}

# Function to check status
check_status() {
    echo "Traffic Generator Status:"
    echo "========================"
    
    if docker compose ps | grep -q "traffic-forge.*running"; then
        echo "✓ Generator is running"
        echo ""
        docker compose ps
        echo ""
        
        # Check for recent log files
        if [ -d ./logs ]; then
            echo "Recent log files:"
            find ./logs -name "*.log" -type f -mmin -60 | head -5
        fi
    else
        echo "✗ Generator is not running"
        echo ""
        echo "Start with: $0 start"
    fi
}

# Function to clean logs
clean_logs() {
    echo "WARNING: This will remove all generated log files!"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo "Removing log files..."
        rm -rf ./logs/*
        echo "✓ Log files removed!"
    else
        echo "Cancelled."
    fi
}

# Main script logic
case "${1:-}" in
    init)
        init_config
        ;;
    start)
        start_generator
        ;;
    stop)
        stop_generator
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    clean)
        clean_logs
        ;;
    *)
        usage
        ;;
esac