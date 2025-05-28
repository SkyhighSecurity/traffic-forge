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
        
        # Initialize user generator with cache file
        domain = self.config['enterprise']['domain']
        cache_file = config_dir / "users.json"
        self.user_generator = UserGenerator(domain, cache_file=cache_file)
        
        # Generate a pool of users matching enterprise configuration
        user_count = self.config['enterprise'].get('total_users', 5000)
        self.users = self.user_generator.generate_users(user_count)
        
        # For performance in realtime mode, create an active user subset
        # This represents users who are currently active (e.g., during business hours)
        # Typically 10-20% of users are active at any given time
        active_user_percentage = 0.15  # 15% of users active
        self.active_user_count = max(1, int(user_count * active_user_percentage))
        
        # Randomly select the active users for this session
        self.active_users = random.sample(self.users, min(self.active_user_count, len(self.users)))
        
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
        
        print(f"Loaded {user_count} total users from enterprise configuration")
        print(f"Using {len(self.active_users)} active users for this session")
        print(f"Loaded {len(self.services)} cloud services")
        
        # Track when we last rotated users (for shift changes)
        self.last_user_rotation = datetime.now()
        self.rotation_interval = timedelta(hours=4)  # Rotate active users every 4 hours
    
    def run(self, display_mode: str = "both"):
        """Run the real-time generator."""
        self.running = True
        
        # Organize logs by date
        today = datetime.now()
        date_dir = self.output_dir / today.strftime('%Y-%m-%d')
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Create hourly log file
        output_file = date_dir / f"traffic_{today.strftime('%Y-%m-%d_%H')}.log"
        
        print(f"Generating real-time logs...")
        print(f"Output: {output_file}")
        print(f"Speed: {self.speed_multiplier}x")
        print("Press Ctrl+C to stop\n")
        
        current_hour = today.hour
        f = open(output_file, 'a')
        
        try:
            event_count = 0
            start_time = time.time()
            
            while self.running:
                # Check if we should rotate active users (shift change)
                current_time = datetime.now()
                if current_time - self.last_user_rotation > self.rotation_interval:
                    self._rotate_active_users()
                    self.last_user_rotation = current_time
                
                # Check if hour changed (rotate log file)
                if current_time.hour != current_hour:
                    f.close()
                    date_dir = self.output_dir / current_time.strftime('%Y-%m-%d')
                    date_dir.mkdir(parents=True, exist_ok=True)
                    output_file = date_dir / f"traffic_{current_time.strftime('%Y-%m-%d_%H')}.log"
                    f = open(output_file, 'a')
                    current_hour = current_time.hour
                    print(f"\n[Log Rotation] New log file: {output_file}\n")
                
                # Generate some events
                timestamp = current_time
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
        
        finally:
            f.close()
        
        print(f"\nGenerated {event_count} events")
    
    def _rotate_active_users(self):
        """Rotate active users to simulate shift changes."""
        # Keep 50% of current active users (overlap between shifts)
        keep_count = len(self.active_users) // 2
        continuing_users = random.sample(self.active_users, keep_count)
        
        # Add new users for the new shift
        new_count = self.active_user_count - keep_count
        available_users = [u for u in self.users if u not in continuing_users]
        new_users = random.sample(available_users, min(new_count, len(available_users)))
        
        self.active_users = continuing_users + new_users
        print(f"\n[Shift Change] Rotated active users: {keep_count} continuing, {len(new_users)} new\n")
    
    def _generate_event(self, timestamp: datetime) -> dict:
        """Generate a random event."""
        # Select a user from the active users
        # This ensures we're reusing the same pool of users throughout the session
        user = random.choice(self.active_users)
        
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