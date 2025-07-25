"""
MCP Client module for Seneca

Provides Marcus client instances using appropriate transport.
"""

import asyncio
import logging
from typing import Optional, Union

from .marcus_client import MarcusClient, MarcusLogReader
from .marcus_http_client import MarcusHttpClient
from .marcus_client_factory import MarcusClientFactory

logger = logging.getLogger(__name__)

# Global instances
marcus_client: Optional[Union[MarcusClient, MarcusHttpClient]] = None
marcus_log_reader = MarcusLogReader()


def get_marcus_client() -> Optional[Union[MarcusClient, MarcusHttpClient]]:
    """Get the global Marcus client instance"""
    return marcus_client


async def initialize_marcus_client(
    transport: str = "auto",
    server_path: Optional[str] = None,
    http_url: Optional[str] = None,
    auto_discover: bool = True
) -> bool:
    """
    Initialize the global Marcus client
    
    Parameters
    ----------
    transport : str
        Transport type: "stdio", "http", or "auto"
    server_path : Optional[str]
        Path for stdio server
    http_url : Optional[str]
        HTTP endpoint URL
    auto_discover : bool
        Enable auto-discovery
        
    Returns
    -------
    bool
        True if connection successful
    """
    global marcus_client
    
    try:
        # Create and connect client
        client = await MarcusClientFactory.create_and_connect(
            transport=transport,
            server_path=server_path,
            http_url=http_url,
            auto_discover=auto_discover
        )
        
        if client:
            marcus_client = client
            logger.info(f"Marcus client initialized with {type(client).__name__}")
            return True
        else:
            logger.error("Failed to initialize Marcus client")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing Marcus client: {e}")
        return False


# For backward compatibility
__all__ = [
    'marcus_client',
    'marcus_log_reader',
    'get_marcus_client',
    'initialize_marcus_client',
    'MarcusClient',
    'MarcusHttpClient',
    'MarcusClientFactory'
]