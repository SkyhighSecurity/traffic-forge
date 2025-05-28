# Skyhigh Traffic Forge

Generate realistic web gateway traffic logs for CASB (Cloud Access Security Broker) testing and demonstrations. Built for Skyhigh Security's CASB demo system.

## Features

- Generate realistic web gateway logs in LEEF and CEF formats
- 500 pre-configured cloud service definitions
- Configurable enterprise settings and user behavior profiles
- Real-time and batch generation modes
- Docker support with volume-based configuration
- Realistic timing patterns and user sessions
- Mixed cloud service and junk traffic for authenticity

## Quick Start

### Using Docker Compose (Recommended)

1. **Download and initialize**:
   ```bash
   # Download docker-compose.yml
   curl -LO https://raw.githubusercontent.com/skyhighsecurity/traffic-forge/main/docker-compose.yml
   
   # Create required directories
   mkdir -p config logs
   
   # Initialize configuration
   docker run --rm -v $(pwd)/config:/etc/skyhigh-traffic-forge \
     ghcr.io/skyhighsecurity/traffic-forge:latest init
   ```

2. **Configure your organization**:
   ```bash
   # Edit the configuration file (relative to current directory)
   nano ./config/enterprise.yaml
   ```

3. **Start generating logs**:
   ```bash
   # Start the generator
   docker compose up -d
   
   # View logs
   docker compose logs -f
   
   # Stop the generator
   docker compose down
   ```

### Using the Quick-Start Script (Optional)

For convenience, you can also use the quick-start script:
```bash
# Download the script
curl -LO https://raw.githubusercontent.com/skyhighsecurity/traffic-forge/main/quick-start.sh
chmod +x quick-start.sh

# Commands available
./quick-start.sh init    # Initialize configuration
./quick-start.sh start   # Start generator
./quick-start.sh stop    # Stop generator
./quick-start.sh logs    # View logs
./quick-start.sh status  # Check status
```


### Using Docker (Manual)

1. **Initialize Configuration**
   ```bash
   # Create a directory for your configuration
   mkdir -p ~/shadow-it-config
   
   # Initialize with default configuration
   docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
     skyhigh-traffic-forge init
   ```

2. **Customize Configuration**
   ```bash
   # Edit the enterprise configuration
   vi ~/shadow-it-config/enterprise.yaml
   ```

3. **Generate Logs**
   ```bash
   # Real-time generation
   docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
     -v ~/shadow-it-logs:/var/log/skyhigh-traffic-forge \
     skyhigh-traffic-forge generate --mode realtime
   
   # Batch generation for last 7 days
   docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
     -v ~/shadow-it-logs:/var/log/skyhigh-traffic-forge \
     skyhigh-traffic-forge generate --mode batch --duration 7d
   ```

### Local Installation

1. **Install**
   ```bash
   pip install -r requirements.txt
   python setup.py install
   ```

2. **Initialize Configuration**
   ```bash
   skyhigh-traffic-forge init --config-dir ./config
   ```

3. **Generate Logs**
   ```bash
   # Real-time generation
   skyhigh-traffic-forge generate --mode realtime --config-dir ./config
   
   # Batch generation
   skyhigh-traffic-forge generate --mode batch --duration 24h --config-dir ./config
   ```

## Configuration

### Docker Volumes

The Docker image uses two volumes:

- `/etc/skyhigh-traffic-forge` - Configuration directory (mount your config here)
- `/var/log/skyhigh-traffic-forge` - Output directory for generated logs

### Configuration Files

After initialization, your configuration directory will contain:

```
config/
├── enterprise.yaml           # Main configuration file
├── enterprise.yaml.example   # Example template
├── cloud-services/          # Cloud service definitions (499 files)
│   ├── slack.yaml
│   ├── dropbox.yaml
│   └── ...
└── junk_sites.json          # Popular website database
```

### Enterprise Configuration

Edit `enterprise.yaml` to customize:

- Enterprise name and domain
- Total number of users
- Network settings (internal subnets, proxy IPs)
- User behavior profiles
- Traffic patterns
- Junk traffic settings

## Usage Examples

### Real-Time Generation with Speed Multiplier

```bash
# Generate logs at 60x speed (1 hour = 1 minute)
docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
  -v ~/shadow-it-logs:/var/log/skyhigh-traffic-forge \
  skyhigh-traffic-forge generate --mode realtime --speed 60
```

### Batch Generation for Specific Period

```bash
# Generate logs for the last 30 days
docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
  -v ~/shadow-it-logs:/var/log/skyhigh-traffic-forge \
  skyhigh-traffic-forge generate --mode batch --duration 30d
```

### Console Output Only (Testing)

```bash
# Display logs in console without writing to file
docker run -v ~/shadow-it-config:/etc/skyhigh-traffic-forge \
  skyhigh-traffic-forge generate --mode realtime --display console
```

## Command Line Options

### `init` Command
- `--config-dir PATH` - Configuration directory (default: /etc/shadow-it-generator)
- `--force` - Overwrite existing configuration

### `generate` Command
- `--mode {batch,realtime}` - Generation mode
- `--config-dir PATH` - Configuration directory
- `--output-dir PATH` - Output directory for logs
- `--format {leef,cef,both}` - Log format (default: leef)
- `--duration TIME` - Duration for batch mode (e.g., 24h, 7d, 1w)
- `--speed FLOAT` - Speed multiplier for realtime mode
- `--display {console,file,both}` - Display mode for realtime

### `validate` Command
- `--config-dir PATH` - Configuration directory to validate

## Cloud Service Definitions

The generator includes 499 pre-configured cloud services across categories:

- **Sanctioned** (70 services) - Approved enterprise applications
- **Unsanctioned** (332 services) - Shadow IT applications
- **Blocked** (97 services) - Prohibited applications

Each service definition includes:
- Network domains and IP ranges
- Traffic patterns and API endpoints
- User adoption rates
- Security event configurations
- Activity simulation parameters

## Log Formats

### LEEF (Log Event Extended Format)
```
LEEF:2.0|McAfee|Web Gateway|10.15.0.623|302|devTime=May 27 2025 18:04:00.000<TAB>src=10.1.2.3<TAB>dst=52.1.2.3<TAB>usrName=john.doe@acme.com<TAB>request=https://slack.com/api/messages<TAB>action=allowed<TAB>cat=collaboration
```

### CEF (Common Event Format)
```
CEF:0|McAfee|Web Gateway|10.15.0.623|proxy|allowed|1|rt=1716840240000 suser=john.doe@acme.com request=https://slack.com/api/messages act=allowed cat=collaboration
```

## Development

### Project Structure
```
skyhigh-traffic-forge/
├── src/shadow_it_generator/     # Main package (internal name)
│   ├── cli.py                  # Command-line interface
│   ├── config/                 # Configuration handling
│   ├── generators/             # Log generators
│   ├── models/                 # Data models
│   └── formatters/             # Log formatters
├── config/                     # Configuration templates
├── data/                       # Static data files
├── Dockerfile                  # Docker image definition
├── docker-entrypoint.sh        # Docker entrypoint script
├── requirements.txt            # Python dependencies
└── setup.py                    # Package setup
```

### Adding New Cloud Services

1. Create a YAML file in `config/cloud-services/`
2. Follow the existing service definition format
3. Rebuild and reinitialize configuration

## Documentation

- [Docker Compose Guide](DOCKER_COMPOSE_GUIDE.md) - Detailed Docker Compose setup and usage
- [Docker Examples](docker-compose.examples.yml) - Example configurations for various use cases

## Docker Compose Files

This project includes several Docker Compose configurations:

- `docker-compose.yml` - Main configuration for running the traffic generator
- `docker-compose.init.yml` - Initialization-only configuration
- `docker-compose.examples.yml` - Example configurations for different scenarios:
  - Development/testing setup
  - High-volume production deployment
  - Historical data generation
  - SIEM integrations (Splunk, Elasticsearch)
  - Multi-region simulation
  - Compliance testing

## Environment Variables

See `.env.example` for all available environment variables. Key variables include:

- `SKYHIGH_LOG_FORMAT` - Output format (splunk, cef, leef, json)
- `SKYHIGH_USER_COUNT` - Number of simulated users
- `SKYHIGH_EVENTS_PER_MINUTE` - Target event generation rate
- `SKYHIGH_WORKER_THREADS` - Number of worker threads
- `SKYHIGH_LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## License

MIT License - See LICENSE file for details
