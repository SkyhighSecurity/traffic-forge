# Docker Implementation for Shadow IT Log Generator

## Overview

The Shadow IT Log Generator is designed to run primarily through Docker, with a configuration initialization system that allows users to:

1. Initialize a base configuration from the Docker image
2. Customize the configuration on their host system
3. Run the generator with their customized configuration

## Key Components

### 1. Command-Line Interface (`src/shadow_it_generator/cli.py`)

The CLI provides three main commands:

- **`init`** - Initialize configuration directory with base files
- **`generate`** - Generate logs (real-time or batch mode)
- **`validate`** - Validate configuration files

### 2. Configuration Initializer (`src/shadow_it_generator/config/initializer.py`)

- Copies base configuration files to user-specified directory
- Includes all 499 cloud service definitions
- Preserves existing customizations when using `--force`

### 3. Docker Setup

**Dockerfile:**
- Based on Python 3.11 slim image
- Creates dedicated user `shadow-it`
- Defines two volumes:
  - `/etc/shadow-it-generator` - Configuration directory
  - `/var/log/shadow-it-generator` - Output directory
- Includes all configuration templates

**docker-entrypoint.sh:**
- Checks if configuration exists
- If not, prompts user to run initialization
- Provides clear instructions for first-time users

## Usage Workflow

### First-Time Setup

1. **Create configuration directory on host:**
   ```bash
   mkdir -p ~/shadow-it-config
   ```

2. **Initialize configuration:**
   ```bash
   docker run -v ~/shadow-it-config:/etc/shadow-it-generator \
     shadow-it-generator init
   ```
   This copies:
   - `enterprise.yaml` - Main configuration
   - `enterprise.yaml.example` - Template for reference
   - `cloud-services/` - 499 service YAML files
   - `junk_sites.json` - Popular website database

3. **Customize configuration:**
   ```bash
   # Edit enterprise settings
   vi ~/shadow-it-config/enterprise.yaml
   
   # Modify cloud services as needed
   vi ~/shadow-it-config/cloud-services/slack.yaml
   ```

### Running the Generator

**Real-time mode (continuous generation):**
```bash
docker run -v ~/shadow-it-config:/etc/shadow-it-generator \
  -v ~/shadow-it-logs:/var/log/shadow-it-generator \
  shadow-it-generator generate --mode realtime
```

**Batch mode (generate historical logs):**
```bash
docker run -v ~/shadow-it-config:/etc/shadow-it-generator \
  -v ~/shadow-it-logs:/var/log/shadow-it-generator \
  shadow-it-generator generate --mode batch --duration 7d
```

**With speed multiplier (for testing):**
```bash
docker run -v ~/shadow-it-config:/etc/shadow-it-generator \
  -v ~/shadow-it-logs:/var/log/shadow-it-generator \
  shadow-it-generator generate --mode realtime --speed 3600
```

## Configuration Persistence

The volume-based approach ensures:

1. **Configuration persists** between container runs
2. **Easy backup** - just backup the mounted directory
3. **Version control** - configuration can be tracked in git
4. **Multi-environment** - different configs for dev/test/prod

## Directory Structure After Initialization

```
~/shadow-it-config/
├── enterprise.yaml              # Your customized configuration
├── enterprise.yaml.example      # Reference template
├── cloud-services/             # Service definitions
│   ├── slack.yaml              # 499 YAML files
│   ├── dropbox.yaml
│   ├── zoom.yaml
│   └── ...
└── junk_sites.json             # Popular website database
```

## Docker Compose Example

For production deployments, use Docker Compose:

```yaml
version: '3.8'

services:
  shadow-it-generator:
    image: shadow-it-generator:latest
    volumes:
      - ./config:/etc/shadow-it-generator
      - ./logs:/var/log/shadow-it-generator
    environment:
      - SHADOW_IT_LOG_LEVEL=INFO
    command: generate --mode realtime --speed 1
    restart: unless-stopped
```

## Benefits of This Approach

1. **No installation required** - Everything runs in Docker
2. **Clean separation** - Configuration separate from code
3. **Easy updates** - Pull new image without losing config
4. **Scalable** - Run multiple instances with different configs
5. **Portable** - Same setup works on any Docker host

## Troubleshooting

If you see "Configuration not found" error:
1. Ensure volume is mounted correctly
2. Run the `init` command first
3. Check file permissions on mounted directory

If services are missing:
1. Re-run `init` without `--force` to add new services
2. Or use `--force` to completely refresh configuration

## Next Steps

1. Build the Docker image:
   ```bash
   docker build -t shadow-it-generator .
   ```

2. Test the workflow:
   ```bash
   # Initialize
   docker run -v ./test-config:/etc/shadow-it-generator \
     shadow-it-generator init
   
   # Generate logs
   docker run -v ./test-config:/etc/shadow-it-generator \
     -v ./test-logs:/var/log/shadow-it-generator \
     shadow-it-generator generate --mode realtime --display console
   ```

3. Deploy to production with appropriate volume management