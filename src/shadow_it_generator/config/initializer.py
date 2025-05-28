"""Configuration initializer for Skyhigh Traffic Forge."""

import shutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConfigInitializer:
    """Initialize configuration directory with base files."""
    
    def __init__(self, source_dir: Optional[Path] = None):
        """
        Initialize the config initializer.
        
        Args:
            source_dir: Source directory containing template configs.
                       If None, will look for templates in package or project.
        """
        if source_dir:
            self.source_dir = source_dir
        else:
            # Try to find source configs
            self.source_dir = self._find_source_dir()
    
    def _find_source_dir(self) -> Path:
        """Find the source configuration directory."""
        # First, check if we're in development (project root has config/)
        project_root = Path(__file__).parent.parent.parent.parent
        dev_config = project_root / "config"
        
        if dev_config.exists() and (dev_config / "enterprise.yaml.example").exists():
            logger.debug(f"Using development config from: {dev_config}")
            return dev_config
        
        # Check for installed package data
        package_data = Path(__file__).parent / "templates"
        if package_data.exists():
            logger.debug(f"Using package templates from: {package_data}")
            return package_data
        
        # Check common system locations
        system_paths = [
            Path("/usr/share/skyhigh-traffic-forge/config"),
            Path("/opt/skyhigh-traffic-forge/config"),
        ]
        
        for path in system_paths:
            if path.exists() and (path / "enterprise.yaml.example").exists():
                logger.debug(f"Using system config from: {path}")
                return path
        
        raise RuntimeError("Cannot find source configuration files")
    
    def initialize(self, target_dir: Path, force: bool = False) -> bool:
        """
        Initialize configuration directory.
        
        Args:
            target_dir: Target directory to initialize
            force: Force overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy enterprise.yaml.example
            src_enterprise = self.source_dir / "enterprise.yaml.example"
            if src_enterprise.exists():
                dst_example = target_dir / "enterprise.yaml.example"
                dst_config = target_dir / "enterprise.yaml"
                
                # Always copy the example
                shutil.copy2(src_enterprise, dst_example)
                logger.info(f"Copied {src_enterprise} to {dst_example}")
                
                # Copy as active config if doesn't exist or force
                if not dst_config.exists() or force:
                    shutil.copy2(src_enterprise, dst_config)
                    logger.info(f"Created {dst_config}")
            
            # Copy cloud-services directory
            src_services = self.source_dir / "cloud-services"
            dst_services = target_dir / "cloud-services"
            
            if src_services.exists():
                if dst_services.exists() and force:
                    shutil.rmtree(dst_services)
                
                if not dst_services.exists():
                    shutil.copytree(src_services, dst_services)
                    logger.info(f"Copied cloud services to {dst_services}")
                else:
                    # Merge new services without overwriting existing
                    self._merge_services(src_services, dst_services)
            
            # Copy junk_sites.json from data directory
            # Look for it in the parent of source dir
            data_locations = [
                self.source_dir.parent / "data" / "junk_sites.json",
                Path(__file__).parent.parent.parent.parent / "data" / "junk_sites.json",
                Path("/usr/share/skyhigh-traffic-forge/data/junk_sites.json"),
            ]
            
            src_junk = None
            for loc in data_locations:
                if loc.exists():
                    src_junk = loc
                    break
            
            if src_junk:
                dst_junk = target_dir / "junk_sites.json"
                if not dst_junk.exists() or force:
                    shutil.copy2(src_junk, dst_junk)
                    logger.info(f"Copied junk sites data to {dst_junk}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            return False
    
    def _merge_services(self, src_dir: Path, dst_dir: Path) -> None:
        """
        Merge cloud services without overwriting existing ones.
        
        Args:
            src_dir: Source services directory
            dst_dir: Destination services directory
        """
        for src_file in src_dir.glob("*.yaml"):
            dst_file = dst_dir / src_file.name
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                logger.debug(f"Added new service: {src_file.name}")