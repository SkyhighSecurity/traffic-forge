"""Batch log generator."""

from pathlib import Path
from datetime import datetime, timedelta
import random
import yaml
from ..utils.user_generator import UserGenerator
from ..utils.ip_generator import IPGenerator
from ..formatters.base import LogEvent
from ..formatters.leef import LEEFFormatter


class BatchGenerator:
    """Simplified batch generator for CLI."""
    
    def __init__(self, config_dir: Path, output_dir: Path):
        self.config_dir = config_dir
        self.output_dir = output_dir
        
        # Load configuration
        with open(config_dir / "enterprise.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize user generator with cache file
        domain = self.config['enterprise']['domain']
        cache_file = config_dir / "users.json"
        self.user_generator = UserGenerator(domain, cache_file=cache_file)
        
        # Initialize IP generator
        network_config = self.config.get('network', {})
        self.ip_generator = IPGenerator(
            internal_subnets=network_config.get('internal_subnets', ['10.0.0.0/8']),
            egress_ips=network_config.get('egress_ips', ['203.0.113.1']),
            proxy_ips=network_config.get('proxy_ips', []),
            vpn_subnets=network_config.get('vpn_subnets', [])
        )
        
        # Initialize LEEF formatter
        self.leef_formatter = LEEFFormatter(output_dir)
        
        # Generate users from cache
        user_count = self.config['enterprise'].get('total_users', 5000)
        self.users = self.user_generator.generate_users(user_count)
        
        # Assign IP addresses to users
        for user in self.users:
            user['ip_address'] = self.ip_generator.generate_internal_ip()
        
        # Load some services
        self.services = []
        services_dir = config_dir / "cloud-services"
        for yaml_file in list(services_dir.glob("*.yaml"))[:50]:  # Load first 50
            with open(yaml_file, 'r') as f:
                self.services.append(yaml.safe_load(f))
    
    def generate(self, start_time: datetime, end_time: datetime, format: str = "leef") -> Path:
        """Generate batch logs for time period."""
        # Use date-based directory structure
        date_dir = self.output_dir / start_time.strftime('%Y-%m-%d')
        date_dir.mkdir(parents=True, exist_ok=True)
        output_file = date_dir / f"batch_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.log"
        
        print(f"Generating batch logs...")
        print(f"Period: {start_time} to {end_time}")
        
        event_count = 0
        with open(output_file, 'w') as f:
            current_time = start_time
            
            while current_time < end_time:
                # Generate events for this time slot
                events_per_slot = random.randint(10, 50)
                
                for _ in range(events_per_slot):
                    # Add some randomness to timestamp
                    event_time = current_time + timedelta(seconds=random.randint(0, 300))
                    event = self._generate_event(event_time)
                    
                    # Use the LEEF formatter
                    line = self.leef_formatter.format_event(event)
                    
                    f.write(line + '\n')
                    event_count += 1
                
                # Move to next 5-minute slot
                current_time += timedelta(minutes=5)
                
                # Show progress
                if event_count % 1000 == 0:
                    progress = (current_time - start_time) / (end_time - start_time) * 100
                    print(f"Progress: {progress:.1f}% ({event_count} events)")
        
        print(f"Generated {event_count} events")
        return output_file
    
    def _generate_event(self, timestamp: datetime) -> LogEvent:
        """Generate a random event."""
        service = random.choice(self.services)
        user = random.choice(self.users)
        
        # Common user agent strings
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        
        domain = random.choice(service['network']['domains']).replace('*.', '')
        action = 'blocked' if service['service']['status'] == 'blocked' else 'allowed'
        
        # Get destination IP from service ranges or generate CDN IP
        service_ip_ranges = service['network'].get('ip_ranges', [])
        dest_ip = self.ip_generator.generate_destination_ip(service_ip_ranges)
        
        # Generate request details
        methods = ['GET'] * 85 + ['POST'] * 10 + ['PUT'] * 3 + ['DELETE'] * 2
        method = random.choice(methods)
        
        # Generate bytes transferred
        if method == 'GET':
            bytes_sent = random.randint(200, 2000)
            bytes_received = random.randint(1000, 100000)
        else:
            bytes_sent = random.randint(1000, 50000)
            bytes_received = random.randint(200, 5000)
        
        # Response time in milliseconds
        duration_ms = random.randint(50, 2000)
        
        return LogEvent(
            timestamp=timestamp,
            source_ip=user['ip_address'],
            destination_ip=dest_ip,
            source_port=self.ip_generator.generate_source_port(),
            destination_port=self.ip_generator.get_destination_port('https'),
            username=user['email'],
            user_domain=self.config['enterprise']['domain'],
            url=f"https://{domain}/",
            method=method,
            status_code=200 if action == 'allowed' else 403,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            duration_ms=duration_ms,
            user_agent=random.choice(user_agents),
            referrer=None,
            action=action,
            category=service['service']['category'],
            risk_level=service['service'].get('risk_level', 'low'),
            service_name=service['service']['name'],
            protocol='https'
        )