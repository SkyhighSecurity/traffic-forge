"""Batch log generator."""

from pathlib import Path
from datetime import datetime, timedelta
import random
import yaml


class BatchGenerator:
    """Simplified batch generator for CLI."""
    
    def __init__(self, config_dir: Path, output_dir: Path):
        self.config_dir = config_dir
        self.output_dir = output_dir
        
        # Load configuration
        with open(config_dir / "enterprise.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load some services
        self.services = []
        services_dir = config_dir / "cloud-services"
        for yaml_file in list(services_dir.glob("*.yaml"))[:50]:  # Load first 50
            with open(yaml_file, 'r') as f:
                self.services.append(yaml.safe_load(f))
    
    def generate(self, start_time: datetime, end_time: datetime, format: str = "leef") -> Path:
        """Generate batch logs for time period."""
        output_file = self.output_dir / f"batch_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.log"
        
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
                    
                    if format == "leef":
                        line = self._format_leef(event)
                    else:
                        line = self._format_cef(event)
                    
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
            'category': service['service']['category'],
            'bytes': random.randint(1000, 100000)
        }
    
    def _format_leef(self, event: dict) -> str:
        """Format as LEEF."""
        header = "LEEF:2.0|McAfee|Web Gateway|10.15.0.623|302|"
        fields = {
            'devTime': event['timestamp'].strftime('%b %d %Y %H:%M:%S'),
            'usrName': event['user'],
            'request': f"https://{event['domain']}/",
            'action': event['action'],
            'cat': event['category'],
            'bytesIn': event['bytes']
        }
        return header + '\t'.join([f"{k}={v}" for k, v in fields.items()])
    
    def _format_cef(self, event: dict) -> str:
        """Format as CEF."""
        header = f"CEF:0|McAfee|Web Gateway|10.15.0.623|proxy|{event['action']}|1|"
        fields = {
            'rt': str(int(event['timestamp'].timestamp() * 1000)),
            'suser': event['user'],
            'request': f"https://{event['domain']}/",
            'act': event['action'],
            'cat': event['category'],
            'in': event['bytes']
        }
        return header + ' '.join([f"{k}={v}" for k, v in fields.items()])