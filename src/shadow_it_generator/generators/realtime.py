"""Real-time log generator."""

from pathlib import Path
import time
import signal
from datetime import datetime, timedelta
import random
import yaml
import json
from ..utils.user_generator import UserGenerator


class RealtimeGenerator:
    """Simplified real-time generator for CLI."""
    
    def __init__(self, config_dir: Path, output_dir: Path, speed_multiplier: float = 1.0):
        self.config_dir = config_dir
        self.output_dir = output_dir
        self.speed_multiplier = speed_multiplier
        self.running = False
        
        # Load configuration
        with open(config_dir / "enterprise.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize user generator
        domain = self.config['enterprise']['domain']
        self.user_generator = UserGenerator(domain)
        
        # Generate a pool of users
        user_count = min(self.config['enterprise'].get('total_users', 5000), 100)  # Cap at 100 for realtime
        self.users = self.user_generator.generate_users(user_count)
        
        # Load cloud services (not junk sites)
        self.services = []
        services_dir = config_dir / "cloud-services"
        service_files = list(services_dir.glob("*.yaml"))
        
        # Load all services but categorize them
        self.sanctioned_services = []
        self.unsanctioned_services = []
        self.blocked_services = []
        
        for yaml_file in service_files:
            with open(yaml_file, 'r') as f:
                service = yaml.safe_load(f)
                self.services.append(service)
                
                # Categorize by status
                status = service['service']['status']
                if status == 'sanctioned':
                    self.sanctioned_services.append(service)
                elif status == 'unsanctioned':
                    self.unsanctioned_services.append(service)
                elif status == 'blocked':
                    self.blocked_services.append(service)
        
        # Setup signal handler
        signal.signal(signal.SIGINT, lambda s, f: setattr(self, 'running', False))
    
    def run(self, display_mode: str = "both"):
        """Run the real-time generator."""
        self.running = True
        output_file = self.output_dir / f"realtime_{datetime.now().strftime('%Y%m%d')}.log"
        
        print(f"Generating real-time logs...")
        print(f"Output: {output_file}")
        print(f"Speed: {self.speed_multiplier}x")
        print("Press Ctrl+C to stop\n")
        
        with open(output_file, 'a') as f:
            event_count = 0
            start_time = time.time()
            
            while self.running:
                # Generate some events
                timestamp = datetime.now()
                events_per_cycle = random.randint(1, 5)
                
                for _ in range(events_per_cycle):
                    event = self._generate_event(timestamp)
                    leef_line = self._format_leef(event)
                    
                    if display_mode in ["console", "both"]:
                        print(f"[{timestamp.strftime('%H:%M:%S')}] {event['user']} -> {event['service']}")
                    
                    if display_mode in ["file", "both"]:
                        f.write(leef_line + '\n')
                        f.flush()
                    
                    event_count += 1
                
                # Show stats periodically
                if event_count % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = event_count / elapsed
                    print(f"\n--- {event_count} events | {rate:.1f} events/sec ---\n")
                
                # Sleep based on speed multiplier
                time.sleep(1.0 / self.speed_multiplier)
        
        print(f"\nGenerated {event_count} events")
    
    def _generate_event(self, timestamp: datetime) -> dict:
        """Generate a random event."""
        # Select a user
        user = random.choice(self.users)
        
        # Decide type of traffic (70% cloud services, 30% junk/internet)
        if random.random() < 0.7 and self.services:
            # Cloud service traffic
            # Choose service based on user type simulation
            rand = random.random()
            if rand < 0.6 and self.sanctioned_services:  # 60% sanctioned
                service = random.choice(self.sanctioned_services)
            elif rand < 0.9 and self.unsanctioned_services:  # 30% unsanctioned
                service = random.choice(self.unsanctioned_services)
            elif self.blocked_services:  # 10% blocked
                service = random.choice(self.blocked_services)
            else:
                service = random.choice(self.services)
            
            domain = random.choice(service['network']['domains']).replace('*.', '')
            action = 'blocked' if service['service']['status'] == 'blocked' else 'allowed'
            
            return {
                'timestamp': timestamp,
                'user': user['email'],
                'service': service['service']['name'],
                'domain': domain,
                'action': action,
                'category': service['service']['category']
            }
        else:
            # Junk/internet traffic
            junk_sites = [
                {'domain': 'news.ycombinator.com', 'category': 'technology'},
                {'domain': 'reddit.com', 'category': 'social'},
                {'domain': 'stackoverflow.com', 'category': 'technology'},
                {'domain': 'medium.com', 'category': 'blogs'},
                {'domain': 'twitter.com', 'category': 'social'},
                {'domain': 'linkedin.com', 'category': 'business'},
                {'domain': 'github.com', 'category': 'development'},
                {'domain': 'youtube.com', 'category': 'streaming'},
                {'domain': 'wikipedia.org', 'category': 'reference'},
                {'domain': 'amazon.com', 'category': 'shopping'}
            ]
            
            site = random.choice(junk_sites)
            
            return {
                'timestamp': timestamp,
                'user': user['email'],
                'service': 'Internet',
                'domain': site['domain'],
                'action': 'allowed',
                'category': site['category']
            }
    
    def _format_leef(self, event: dict) -> str:
        """Format as LEEF."""
        header = "LEEF:2.0|McAfee|Web Gateway|10.15.0.623|302|"
        fields = {
            'devTime': event['timestamp'].strftime('%b %d %Y %H:%M:%S.%f')[:-3],
            'usrName': event['user'],
            'request': f"https://{event['domain']}/",
            'action': event['action'],
            'cat': event['category']
        }
        return header + '\t'.join([f"{k}={v}" for k, v in fields.items()])