"""Cloud service model."""

from typing import Dict, Any, List, Optional


class CloudService:
    """Cloud service configuration."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.service = data.get("service", {})
        self.network = data.get("network", {})
        self.traffic_patterns = data.get("traffic_patterns", {})
        self.activity = data.get("activity", {})
        self.security_events = data.get("security_events", {})
        self.traffic_override = data.get("traffic_override", {})
    
    @property
    def name(self) -> str:
        """Get service name."""
        return self.service.get("name", "unknown")
    
    @property
    def status(self) -> str:
        """Get service status."""
        return self.service.get("status", "unsanctioned")
    
    @property
    def category(self) -> str:
        """Get service category."""
        return self.service.get("category", "other")
    
    @property
    def risk_level(self) -> str:
        """Get service risk level."""
        return self.service.get("risk_level", "low")
    
    @property
    def domains(self) -> List[str]:
        """Get service domains."""
        return self.network.get("domains", [])
    
    @property
    def user_adoption_rate(self) -> float:
        """Get user adoption rate."""
        return self.activity.get("user_adoption_rate", 0.1)
    
    @property
    def block_rate(self) -> float:
        """Get block rate."""
        return self.security_events.get("block_rate", 0.0)
    
    @property
    def has_traffic_override(self) -> bool:
        """Check if service has traffic override configuration."""
        return bool(self.traffic_override)
    
    @property
    def override_access_count(self) -> Optional[Dict[str, float]]:
        """Get override access count per hour by user profile.
        
        Returns:
            Dict with 'mean' and 'std' for access count, or None if not set.
        """
        return self.traffic_override.get("access_count_per_hour")
    
    @property
    def override_bandwidth(self) -> Optional[Dict[str, Any]]:
        """Get override bandwidth usage per user.
        
        Returns:
            Dict with bandwidth configuration by profile, or None if not set.
        """
        return self.traffic_override.get("bandwidth_per_user")