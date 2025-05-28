"""Real-time log generator."""

from pathlib import Path
import time
import signal
from datetime import datetime, timedelta
import random
import yaml
import json


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
        
        # Load some services
        self.services = []
        services_dir = config_dir / "cloud-services"
        for yaml_file in list(services_dir.glob("*.yaml"))[:50]:  # Load first 50
            with open(yaml_file, 'r') as f:
                self.services.append(yaml.safe_load(f))
        
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
        service = random.choice(self.services)
        domain = self.config['enterprise']['domain']
        
        return {
            'timestamp': timestamp,
            'user': f"user{random.randint(1,100)}@{domain}",
            'service': service['service']['name'],
            'domain': service['network']['domains'][0].replace('*.', ''),
            'action': 'blocked' if random.random() < 0.1 else 'allowed',
            'category': service['service']['category']
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