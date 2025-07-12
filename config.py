"""
Configuration module for Seneca visualization platform.

This module handles all configuration settings for Seneca, including
paths, API settings, and feature flags. Configuration can be set via
environment variables or configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


class SenecaConfig:
    """
    Central configuration class for Seneca.
    
    Handles configuration from environment variables, config files,
    and provides defaults for all settings.
    
    Attributes:
        marcus_log_dir: Path to Marcus conversation log directory
        host: Server host address
        port: Server port number
        debug: Debug mode flag
        
    Example:
        >>> config = SenecaConfig()
        >>> config.marcus_log_dir
        '/path/to/marcus/logs/conversations'
        
        >>> # Override with environment variable
        >>> os.environ['MARCUS_LOG_DIR'] = '/custom/path'
        >>> config = SenecaConfig()
        >>> config.marcus_log_dir
        '/custom/path'
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self._config_file = config_file
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment and files."""
        # Marcus integration settings
        self.marcus_log_dir: str = self._get_config(
            'MARCUS_LOG_DIR',
            default=str(Path.home() / 'dev' / 'marcus' / 'logs' / 'conversations')
        )
        
        # Validate Marcus log directory exists
        if not Path(self.marcus_log_dir).exists():
            # Try relative path from Seneca root
            relative_path = Path(__file__).parent.parent / 'marcus' / 'logs' / 'conversations'
            if relative_path.exists():
                self.marcus_log_dir = str(relative_path)
            else:
                print(f"Warning: Marcus log directory not found at {self.marcus_log_dir}")
        
        # Server settings
        self.host: str = self._get_config('SENECA_HOST', default='0.0.0.0')
        self.port: int = int(self._get_config('SENECA_PORT', default='8080'))
        self.debug: bool = self._get_config('SENECA_DEBUG', default='false').lower() == 'true'
        
        # UI settings
        self.ui_refresh_interval: int = int(self._get_config('UI_REFRESH_INTERVAL', default='1000'))
        self.max_conversations_display: int = int(self._get_config('MAX_CONVERSATIONS_DISPLAY', default='100'))
        
        # Feature flags
        self.enable_websocket: bool = self._get_config('ENABLE_WEBSOCKET', default='true').lower() == 'true'
        self.enable_analytics: bool = self._get_config('ENABLE_ANALYTICS', default='true').lower() == 'true'
        self.enable_export: bool = self._get_config('ENABLE_EXPORT', default='true').lower() == 'true'
        
        # Caching settings
        self.cache_ttl: int = int(self._get_config('CACHE_TTL', default='300'))  # 5 minutes
        self.cache_size: int = int(self._get_config('CACHE_SIZE', default='1000'))
        
        # Theme settings
        self.default_theme: str = self._get_config('DEFAULT_THEME', default='dark')
        
    def _get_config(self, key: str, default: str = '') -> str:
        """
        Get configuration value from environment or default.
        
        Args:
            key: Configuration key to look up
            default: Default value if not found
            
        Returns:
            Configuration value as string
        """
        # First check environment variable
        if key in os.environ:
            return os.environ[key]
        
        # TODO: Add support for config file loading
        # if self._config_file and self._file_config:
        #     return self._file_config.get(key, default)
        
        return default
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary of all configuration values
        """
        return {
            'marcus_log_dir': self.marcus_log_dir,
            'host': self.host,
            'port': self.port,
            'debug': self.debug,
            'ui_refresh_interval': self.ui_refresh_interval,
            'max_conversations_display': self.max_conversations_display,
            'enable_websocket': self.enable_websocket,
            'enable_analytics': self.enable_analytics,
            'enable_export': self.enable_export,
            'cache_ttl': self.cache_ttl,
            'cache_size': self.cache_size,
            'default_theme': self.default_theme
        }
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check Marcus log directory
        if not Path(self.marcus_log_dir).exists():
            raise ValueError(f"Marcus log directory does not exist: {self.marcus_log_dir}")
        
        # Check port range
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        
        # Check refresh interval
        if self.ui_refresh_interval < 100:
            raise ValueError(f"UI refresh interval too low: {self.ui_refresh_interval}ms")
        
        return True


# Global configuration instance
config = SenecaConfig()


# Convenience functions for accessing config
def get_marcus_log_dir() -> str:
    """Get Marcus log directory path."""
    return config.marcus_log_dir


def get_server_config() -> Dict[str, Any]:
    """Get server configuration for Flask."""
    return {
        'host': config.host,
        'port': config.port,
        'debug': config.debug
    }


def get_ui_config() -> Dict[str, Any]:
    """Get UI configuration for frontend."""
    return {
        'refresh_interval': config.ui_refresh_interval,
        'max_conversations': config.max_conversations_display,
        'enable_websocket': config.enable_websocket,
        'enable_analytics': config.enable_analytics,
        'enable_export': config.enable_export,
        'default_theme': config.default_theme
    }