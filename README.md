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
- Traffic override configurations (optional)

## Log Formats

### LEEF (Log Event Extended Format)

LEEF format with all McAfee Web Gateway fields (tab-separated):
```
LEEF:2.0|McAfee|Web Gateway|12.2.19|302|devTime=May 27 2025 18:04:00.000	src=10.1.2.3	dst=52.1.2.3	srcPort=45123	dstPort=443	usrName=john.doe@acme.com	domain=acme.com	request=https://slack.com/api/messages	method=GET	proto=https	status=200	action=allowed	cat=collaboration	riskLevel=low	bytesIn=45678	bytesOut=1234	responseTime=523	userAgent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36	app=Slack
```

**LEEF Fields:**
- `devTime` - Event timestamp
- `src` - Source IP address (internal user IP)
- `dst` - Destination IP address (cloud service IP)
- `srcPort` - Source port (ephemeral port)
- `dstPort` - Destination port (typically 443 for HTTPS)
- `usrName` - Username with email format
- `domain` - User's domain
- `request` - Full URL requested
- `method` - HTTP method (GET, POST, etc.)
- `proto` - Protocol (https/http)
- `status` - HTTP status code
- `action` - Action taken (allowed/blocked)
- `cat` - Service category
- `riskLevel` - Risk assessment (low/medium/high)
- `bytesIn` - Bytes received
- `bytesOut` - Bytes sent
- `responseTime` - Response time in milliseconds
- `userAgent` - Browser user agent string
- `app` - Application/service name (optional)

### CEF (Common Event Format)

CEF format with all fields (space-separated key=value pairs):
```
CEF:0|McAfee|Web Gateway|12.2.19|100|Web request to Slack|1|rt=1716840240000 src=10.1.2.3 dst=52.1.2.3 spt=45123 dpt=443 suser=john.doe@acme.com sntdom=acme.com request=https://slack.com/api/messages requestMethod=GET app=HTTPS flexNumber1=200 flexNumber1Label=HTTPStatus in=45678 out=1234 cn1=523 cn1Label=ResponseTime requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 cat=collaboration act=allowed flexString1=low flexString1Label=RiskLevel destinationServiceName=Slack
```

**CEF Fields:**
- `rt` - Receipt time (milliseconds since epoch)
- `src` - Source IP address
- `dst` - Destination IP address
- `spt` - Source port
- `dpt` - Destination port
- `suser` - Source username
- `sntdom` - Source NT domain
- `request` - Request URL
- `requestMethod` - HTTP method
- `app` - Application protocol
- `flexNumber1` - HTTP status code
- `in` - Bytes in
- `out` - Bytes out
- `cn1` - Response time (custom number 1)
- `requestClientApplication` - User agent
- `cat` - Category
- `act` - Action
- `flexString1` - Risk level
- `destinationServiceName` - Service name

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

### Traffic Override Configuration

For core services that all users access heavily (like Microsoft 365, OneDrive, Slack), you can use traffic overrides to specify exact access patterns instead of relying on weighted random selection:

```yaml
traffic_override:
  access_count_per_hour:
    normal:
      mean: 25    # Average accesses per hour
      std: 5      # Standard deviation
    power_user:
      mean: 40
      std: 10
    risky:
      mean: 20
      std: 8
  bandwidth_per_user:
    normal:
      daily_mb: 500           # Daily bandwidth usage
      peak_multiplier: 2.5    # Peak hour multiplier
    power_user:
      daily_mb: 1500
      peak_multiplier: 3.0
    risky:
      daily_mb: 300
      peak_multiplier: 2.0
```

Services with traffic overrides will:
- Always be accessed by assigned users (not subject to random selection)
- Generate the specified number of accesses per hour based on user profile
- Use defined bandwidth patterns for realistic traffic volume

Core services with pre-configured overrides:
- **Microsoft 365**: Heavy usage throughout the workday (25-40 accesses/hour)
- **OneDrive**: File sync and storage patterns (15-30 accesses/hour)
- **Slack**: Continuous messaging activity (30-50 accesses/hour)
- **Google Workspace**: Email and collaboration (20-35 accesses/hour)
- **Salesforce**: Periodic CRM access (8-20 accesses/hour)

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
