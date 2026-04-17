"""
Proxy Manager - Load and rotate proxies from file
Supports multiple proxies with automatic rotation and health checking
"""

import logging
import random
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProxyStats:
    """Statistics for a proxy."""
    proxy_url: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests * 100
    
    @property
    def is_healthy(self) -> bool:
        """Check if proxy is healthy (>50% success rate)."""
        if self.total_requests < 5:
            return True  # Not enough data, assume healthy
        return self.success_rate >= 50.0


class ProxyManager:
    """
    Manages multiple proxies with rotation and health checking.
    
    Features:
    - Load proxies from file
    - Automatic rotation (round-robin or random)
    - Health checking (skip unhealthy proxies)
    - Statistics tracking
    """
    
    def __init__(
        self,
        proxies_file: str = "proxies.txt",
        rotation_mode: str = "round-robin",
        skip_unhealthy: bool = True
    ):
        """
        Initialize ProxyManager.
        
        Args:
            proxies_file: Path to file with proxy URLs (one per line)
            rotation_mode: 'round-robin' or 'random'
            skip_unhealthy: Skip proxies with <50% success rate
        """
        self.proxies_file = Path(proxies_file)
        self.rotation_mode = rotation_mode
        self.skip_unhealthy = skip_unhealthy
        self.logger = logging.getLogger(__name__)
        
        # Load proxies
        self.proxies: List[str] = []
        self.proxy_stats: Dict[str, ProxyStats] = {}
        self.current_index = 0
        
        self._load_proxies()
    
    def _load_proxies(self) -> None:
        """Load proxies from file."""
        if not self.proxies_file.exists():
            self.logger.warning(f"Proxies file not found: {self.proxies_file}")
            return
        
        try:
            with open(self.proxies_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Validate and normalize proxy format
                # Support both formats:
                # 1. Full URL: http://user:pass@host:port
                # 2. IP:PORT: 1.2.3.4:8080 (will be converted to http://1.2.3.4:8080)
                
                if any(line.startswith(proto) for proto in ['http://', 'https://', 'socks5://']):
                    # Already has protocol
                    proxy_url = line
                elif ':' in line and line.replace('.', '').replace(':', '').isdigit():
                    # IP:PORT format, add http:// prefix
                    proxy_url = f"http://{line}"
                    self.logger.debug(f"Normalized proxy: {line} -> {proxy_url}")
                else:
                    self.logger.warning(f"Invalid proxy format (skipped): {line}")
                    continue
                
                self.proxies.append(proxy_url)
                self.proxy_stats[proxy_url] = ProxyStats(proxy_url=proxy_url)
                self.proxy_stats[line] = ProxyStats(proxy_url=line)
            
            self.logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxies_file}")
            
            if not self.proxies:
                self.logger.warning("No valid proxies found in file")
        
        except Exception as e:
            self.logger.error(f"Failed to load proxies: {e}")
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Get next proxy based on rotation mode.
        
        Returns:
            Proxy URL or None if no proxies available
        """
        if not self.proxies:
            return None
        
        # Filter healthy proxies if enabled
        available_proxies = self.proxies
        if self.skip_unhealthy:
            healthy_proxies = [
                p for p in self.proxies
                if self.proxy_stats[p].is_healthy
            ]
            if healthy_proxies:
                available_proxies = healthy_proxies
            else:
                self.logger.warning("No healthy proxies available, using all proxies")
        
        # Select proxy based on rotation mode
        if self.rotation_mode == "random":
            proxy = random.choice(available_proxies)
        else:  # round-robin
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1
        
        # Update stats
        self.proxy_stats[proxy].last_used = datetime.now()
        
        return proxy
    
    def report_success(self, proxy: str) -> None:
        """
        Report successful request for proxy.
        
        Args:
            proxy: Proxy URL
        """
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats.total_requests += 1
            stats.successful_requests += 1
            stats.last_success = datetime.now()
    
    def report_failure(self, proxy: str) -> None:
        """
        Report failed request for proxy.
        
        Args:
            proxy: Proxy URL
        """
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats.total_requests += 1
            stats.failed_requests += 1
            stats.last_failure = datetime.now()
    
    def get_stats(self) -> List[ProxyStats]:
        """
        Get statistics for all proxies.
        
        Returns:
            List of ProxyStats sorted by success rate
        """
        stats_list = list(self.proxy_stats.values())
        stats_list.sort(key=lambda s: s.success_rate, reverse=True)
        return stats_list
    
    def print_stats(self) -> None:
        """Print proxy statistics."""
        stats_list = self.get_stats()
        
        print("\n" + "="*80)
        print("PROXY STATISTICS")
        print("="*80)
        print(f"\nTotal proxies: {len(self.proxies)}")
        print(f"Rotation mode: {self.rotation_mode}")
        print(f"Skip unhealthy: {self.skip_unhealthy}")
        print()
        
        if not stats_list:
            print("No statistics available yet")
            print("="*80 + "\n")
            return
        
        # Header
        print(f"{'Proxy':<40} {'Requests':<10} {'Success':<10} {'Failed':<10} {'Rate':<10} {'Status':<10}")
        print("-"*80)
        
        # Stats
        for stats in stats_list:
            proxy_display = stats.proxy_url.split('@')[-1] if '@' in stats.proxy_url else stats.proxy_url
            if len(proxy_display) > 38:
                proxy_display = proxy_display[:35] + "..."
            
            status = "✓ Healthy" if stats.is_healthy else "✗ Unhealthy"
            
            print(f"{proxy_display:<40} {stats.total_requests:<10} {stats.successful_requests:<10} "
                  f"{stats.failed_requests:<10} {stats.success_rate:<9.1f}% {status:<10}")
        
        print("="*80 + "\n")
    
    def reload_proxies(self) -> None:
        """Reload proxies from file."""
        self.logger.info("Reloading proxies...")
        old_count = len(self.proxies)
        
        # Keep existing stats
        old_stats = self.proxy_stats.copy()
        
        # Reload
        self.proxies = []
        self.proxy_stats = {}
        self._load_proxies()
        
        # Restore stats for existing proxies
        for proxy in self.proxies:
            if proxy in old_stats:
                self.proxy_stats[proxy] = old_stats[proxy]
        
        self.logger.info(f"Reloaded: {old_count} -> {len(self.proxies)} proxies")
    
    def has_proxies(self) -> bool:
        """Check if any proxies are available."""
        return len(self.proxies) > 0
    
    def get_proxy_count(self) -> int:
        """Get number of loaded proxies."""
        return len(self.proxies)
