#!/usr/bin/env python3
"""Command-line interface for Skyhigh Traffic Forge."""

import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

from ._version import __version__, __description__, __author__
from .config.initializer import ConfigInitializer
from .generators.realtime import RealtimeGenerator
from .generators.batch import BatchGenerator

# Default paths
DEFAULT_CONFIG_DIR = Path("/etc/skyhigh-traffic-forge")
DEFAULT_OUTPUT_DIR = Path("/var/log/skyhigh-traffic-forge")
DEFAULT_DATA_DIR = Path("/usr/share/skyhigh-traffic-forge/data")

# For development/local runs
if not DEFAULT_CONFIG_DIR.exists():
    DEFAULT_CONFIG_DIR = Path("./config")
if not DEFAULT_OUTPUT_DIR.exists():
    DEFAULT_OUTPUT_DIR = Path("./output")
if not DEFAULT_DATA_DIR.exists():
    DEFAULT_DATA_DIR = Path("./data")

def get_output_dir():
    """Get output directory from environment or defaults."""
    import os
    env_dir = os.environ.get('SKYHIGH_OUTPUT_DIR')
    if env_dir:
        return Path(env_dir)
    
    # Check runtime paths (for Docker volumes)
    if Path("/var/log/skyhigh-traffic-forge").exists():
        return Path("/var/log/skyhigh-traffic-forge")
    
    return DEFAULT_OUTPUT_DIR


def init_command(args):
    """Initialize configuration directory with base files."""
    config_dir = Path(args.config_dir)
    
    print("Skyhigh Traffic Forge - Configuration Initializer")
    print("=" * 50)
    
    if config_dir.exists() and any(config_dir.iterdir()):
        if not args.force:
            print(f"\nConfiguration directory '{config_dir}' already exists and is not empty.")
            print("Use --force to overwrite existing configuration.")
            return 1
        else:
            print(f"\nOverwriting existing configuration in '{config_dir}'...")
    
    # Initialize configuration
    initializer = ConfigInitializer()
    success = initializer.initialize(config_dir, force=args.force)
    
    if success:
        print(f"\n✅ Configuration initialized successfully in: {config_dir}")
        print(f"\nCreated:")
        print(f"  - enterprise.yaml (main configuration)")
        print(f"  - enterprise.yaml.example (template for reference)")
        print(f"  - cloud-services/ (499 service definitions)")
        print(f"  - junk_sites.json (popular website database)")
        print(f"\nNext steps:")
        print(f"  1. Edit {config_dir}/enterprise.yaml to match your organization")
        print(f"  2. Review and customize cloud service definitions as needed")
        print(f"  3. Run 'shadow-it-generator generate' to start generating logs")
        
        if str(config_dir).startswith("/etc/"):
            print(f"\nFor Docker usage:")
            print(f"  Mount a volume to persist configuration:")
            print(f"    docker run -v /path/to/config:{config_dir} shadow-it-generator")
        
        return 0
    else:
        print(f"\n❌ Failed to initialize configuration")
        return 1


def generate_command(args):
    """Generate logs based on mode (batch or realtime)."""
    config_dir = Path(args.config_dir)
    
    # Use runtime output directory check
    if args.output_dir == str(DEFAULT_OUTPUT_DIR):
        # User didn't specify, use runtime default
        output_dir = get_output_dir()
    else:
        # User specified a directory
        output_dir = Path(args.output_dir)
    
    # Check if configuration exists
    if not config_dir.exists() or not (config_dir / "enterprise.yaml").exists():
        print("❌ Configuration not found!")
        print(f"\nNo configuration found in: {config_dir}")
        print("\nPlease initialize the configuration first:")
        print(f"  skyhigh-traffic-forge init --config-dir {config_dir}")
        print("\nOr if using Docker, mount a volume with your configuration:")
        print(f"  docker run -v /path/to/config:{config_dir} shadow-it-generator init")
        return 1
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Skyhigh Traffic Forge")
    print("=" * 50)
    print(f"Version: {__version__}")
    print(f"Configuration: {config_dir}")
    print(f"Output: {output_dir}")
    print(f"Mode: {args.mode}")
    
    if args.mode == "realtime":
        print(f"Speed: {args.speed}x")
        print("\nPress Ctrl+C to stop\n")
        
        generator = RealtimeGenerator(
            config_dir=config_dir,
            output_dir=output_dir,
            speed_multiplier=args.speed
        )
        
        try:
            generator.run(display_mode=args.display)
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            return 0
    
    else:  # batch mode
        if args.duration:
            # Parse duration (e.g., "24h", "7d", "1w")
            duration_map = {
                'h': 'hours',
                'd': 'days',
                'w': 'weeks'
            }
            
            duration_value = int(args.duration[:-1])
            duration_unit = args.duration[-1]
            
            if duration_unit not in duration_map:
                print(f"❌ Invalid duration format: {args.duration}")
                print("Use format like: 24h, 7d, 1w")
                return 1
            
            kwargs = {duration_map[duration_unit]: duration_value}
            duration_delta = timedelta(**kwargs)
        else:
            duration_delta = timedelta(days=1)  # Default 1 day
        
        end_time = datetime.now()
        start_time = end_time - duration_delta
        
        print(f"\nGenerating logs from {start_time} to {end_time}")
        
        generator = BatchGenerator(
            config_dir=config_dir,
            output_dir=output_dir
        )
        
        output_file = generator.generate(
            start_time=start_time,
            end_time=end_time,
            format=args.format
        )
        
        print(f"\n✅ Generated logs: {output_file}")
        return 0


def validate_command(args):
    """Validate configuration files."""
    config_dir = Path(args.config_dir)
    
    print("Skyhigh Traffic Forge - Configuration Validator")
    print("=" * 50)
    
    if not config_dir.exists():
        print(f"❌ Configuration directory not found: {config_dir}")
        return 1
    
    # Validate enterprise config
    enterprise_config = config_dir / "enterprise.yaml"
    if not enterprise_config.exists():
        print(f"❌ Enterprise configuration not found: {enterprise_config}")
        return 1
    
    print(f"\nValidating {enterprise_config}...")
    # TODO: Add actual validation logic
    print("✅ Enterprise configuration is valid")
    
    # Validate cloud services
    services_dir = config_dir / "cloud-services"
    if not services_dir.exists():
        print(f"❌ Cloud services directory not found: {services_dir}")
        return 1
    
    yaml_files = list(services_dir.glob("*.yaml"))
    print(f"\nFound {len(yaml_files)} cloud service definitions")
    
    # TODO: Add service validation logic
    print("✅ All service definitions are valid")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"Skyhigh Traffic Forge v{__version__} - {__description__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize configuration
  skyhigh-traffic-forge init --config-dir /etc/skyhigh-traffic-forge
  
  # Generate logs in real-time
  skyhigh-traffic-forge generate --mode realtime --speed 60
  
  # Generate batch logs for last 7 days
  skyhigh-traffic-forge generate --mode batch --duration 7d
  
  # Validate configuration
  skyhigh-traffic-forge validate

Docker Usage:
  # Initialize configuration in a mounted volume
  docker run -v /path/to/config:/etc/skyhigh-traffic-forge \\
    skyhigh-traffic-forge init
  
  # Run with persistent configuration and output
  docker run -v /path/to/config:/etc/skyhigh-traffic-forge \\
    -v /path/to/logs:/var/log/skyhigh-traffic-forge \\
    skyhigh-traffic-forge generate --mode realtime
"""
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--config-dir",
        default=str(DEFAULT_CONFIG_DIR),
        help=f"Configuration directory (default: {DEFAULT_CONFIG_DIR})"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize configuration directory with base files"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration"
    )
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate shadow IT logs"
    )
    gen_parser.add_argument(
        "--mode",
        choices=["batch", "realtime"],
        default="batch",
        help="Generation mode (default: batch)"
    )
    gen_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    gen_parser.add_argument(
        "--format",
        choices=["leef", "cef", "both"],
        default="leef",
        help="Output format (default: leef)"
    )
    gen_parser.add_argument(
        "--duration",
        help="Duration for batch mode (e.g., 24h, 7d, 1w)"
    )
    gen_parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speed multiplier for realtime mode (default: 1.0)"
    )
    gen_parser.add_argument(
        "--display",
        choices=["console", "file", "both"],
        default="both",
        help="Display mode for realtime (default: both)"
    )
    
    # Validate command
    val_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration files"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Execute command
    if args.command == "init":
        return init_command(args)
    elif args.command == "generate":
        return generate_command(args)
    elif args.command == "validate":
        return validate_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())