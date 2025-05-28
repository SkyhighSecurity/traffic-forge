# Docker Compose Guide for Skyhigh Traffic Forge

This guide explains how to use Docker Compose to run Skyhigh Traffic Forge for generating realistic web gateway traffic logs.

## Prerequisites

- Docker Engine 20.10.0 or higher
- Docker Compose v2.0.0 or higher
- At least 2GB of available disk space for log storage

## Quick Start

1. **Download the docker-compose.yml file**:
   ```bash
   curl -O https://raw.githubusercontent.com/skyhighsecurity/traffic-forge/main/docker-compose.yml
   ```

2. **Initialize the configuration** (first time only):
   ```bash
   docker compose run --rm traffic-forge init
   ```

3. **Edit the configuration**:
   ```bash
   # Edit the main configuration
   nano ./config/enterprise.yaml
   
   # Optionally edit service definitions
   nano ./config/cloud-services/*.yaml
   ```

4. **Start generating logs**:
   ```bash
   # Start in detached mode
   docker compose up -d
   
   # View logs
   docker compose logs -f
   
   # Stop generation
   docker compose down
   ```

## Directory Structure

After initialization, your directory structure will look like:
```
.
├── docker-compose.yml
├── config/
│   ├── enterprise.yaml         # Main configuration
│   └── cloud-services/         # Service definitions
│       ├── salesforce.yaml
│       ├── dropbox.yaml
│       └── ... (300+ services)
└── logs/
    └── traffic/                # Generated log files
        ├── 2024-01-15/
        │   ├── traffic_2024-01-15_00.log
        │   ├── traffic_2024-01-15_01.log
        │   └── ...
        └── ...
```

## Configuration Modes

### 1. Real-time Mode (Default)
Generates logs continuously in real-time, simulating live traffic:
```yaml
command: generate --mode realtime
```

### 2. Batch Mode
Generates a specific time range of historical logs:
```yaml
command: generate --mode batch --start-date 2024-01-01 --end-date 2024-01-31
```

### 3. Replay Mode
Replays a specific date range at accelerated speed:
```yaml
command: generate --mode replay --start-date 2024-01-01 --days 7 --speed 10
```

## Volume Mounts

The docker-compose.yml uses two volumes:

1. **Configuration Volume** (`./config:/etc/skyhigh-traffic-forge`):
   - Contains enterprise.yaml and cloud service definitions
   - Persist your configuration between runs
   - Required for the generator to run

2. **Logs Volume** (`./logs:/var/log/skyhigh-traffic-forge`):
   - Where generated log files are written
   - Organized by date (YYYY-MM-DD folders)
   - Can be mounted read-only by other containers for processing

## Environment Variables

Configure the generator behavior with environment variables:

```yaml
environment:
  # Log output format
  SKYHIGH_LOG_FORMAT: "splunk"  # Options: splunk, cef, leef, json
  
  # Output settings
  SKYHIGH_OUTPUT_DIR: "/var/log/skyhigh-traffic-forge"
  SKYHIGH_MAX_FILE_SIZE: "100MB"
  SKYHIGH_ROTATE_INTERVAL: "1h"
  
  # Performance tuning
  SKYHIGH_WORKER_THREADS: "4"
  SKYHIGH_BATCH_SIZE: "1000"
  
  # Logging level
  SKYHIGH_LOG_LEVEL: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
```

## Advanced Usage

### Multiple Environments

Run multiple instances with different configurations:

```yaml
# docker-compose.multi.yml
services:
  traffic-forge-prod:
    extends:
      file: docker-compose.yml
      service: traffic-forge
    volumes:
      - ./config-prod:/etc/skyhigh-traffic-forge
      - ./logs-prod:/var/log/skyhigh-traffic-forge
    container_name: traffic-forge-prod

  traffic-forge-dev:
    extends:
      file: docker-compose.yml
      service: traffic-forge
    volumes:
      - ./config-dev:/etc/skyhigh-traffic-forge
      - ./logs-dev:/var/log/skyhigh-traffic-forge
    container_name: traffic-forge-dev
```

### Integration with Log Collectors

Example with Fluentd:

```yaml
services:
  traffic-forge:
    # ... traffic forge config ...
    
  fluentd:
    image: fluent/fluentd:v1.16
    volumes:
      - ./logs:/var/log/traffic:ro
      - ./fluentd.conf:/fluentd/etc/fluent.conf
    depends_on:
      - traffic-forge
```

### Health Monitoring

The container includes a health check that monitors log generation:

```yaml
healthcheck:
  test: ["CMD", "test", "-f", "/var/log/skyhigh-traffic-forge/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Resource Limits

For production deployments, set appropriate resource limits:

```yaml
services:
  traffic-forge:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs traffic-forge

# Verify configuration
docker compose run --rm traffic-forge validate
```

### No logs being generated
```bash
# Check if config is mounted correctly
docker compose exec traffic-forge ls -la /etc/skyhigh-traffic-forge/

# Test with debug logging
docker compose run --rm -e SKYHIGH_LOG_LEVEL=DEBUG traffic-forge generate --mode batch --days 1
```

### Permission issues
```bash
# Fix ownership of volumes
sudo chown -R 1000:1000 ./config ./logs
```

## Maintenance

### Backup Configuration
```bash
# Backup config
tar -czf traffic-forge-config-$(date +%Y%m%d).tar.gz ./config/

# Backup specific date range of logs
tar -czf traffic-logs-202401.tar.gz ./logs/traffic/2024-01-*/
```

### Clean Up Old Logs
```bash
# Remove logs older than 30 days
find ./logs/traffic/ -type f -name "*.log" -mtime +30 -delete

# Remove empty directories
find ./logs/traffic/ -type d -empty -delete
```

### Update to Latest Version
```bash
# Pull latest image
docker compose pull

# Restart with new image
docker compose up -d
```

## Security Considerations

1. **Configuration Security**:
   - Keep enterprise.yaml secure (contains org details)
   - Use secrets management for sensitive data
   - Restrict access to config directory

2. **Network Isolation**:
   - Traffic Forge doesn't require network access
   - Can run in isolated network: `network_mode: none`

3. **Read-Only Filesystem**:
   - Mount config as read-only after setup
   - Only logs directory needs write access

## Example Configurations

### Minimal Setup
Just generate logs with default settings:
```bash
docker compose up -d
```

### High-Volume Testing
Generate large amounts of traffic for testing:
```yaml
environment:
  SKYHIGH_USER_COUNT: "10000"
  SKYHIGH_EVENTS_PER_MINUTE: "50000"
```

### SIEM Integration
Format logs for specific SIEM:
```yaml
environment:
  SKYHIGH_LOG_FORMAT: "cef"  # For ArcSight
  # or
  SKYHIGH_LOG_FORMAT: "leef" # For QRadar
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/skyhighsecurity/traffic-forge/issues
- Documentation: https://docs.skyhighsecurity.com/traffic-forge
- Docker Hub: https://hub.docker.com/r/skyhighsecurity/traffic-forge