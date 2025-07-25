"""
Marcus Client Factory for transport selection

This module provides a factory for creating the appropriate Marcus client
based on the desired transport (stdio or HTTP).
"""

import logging
import os
from typing import Optional, Union

from .marcus_client import MarcusClient
from .marcus_http_client import MarcusHttpClient

logger = logging.getLogger(__name__)


class MarcusClientFactory:
    """
    Factory for creating Marcus clients with different transports
    """
    
    @staticmethod
    def create_client(
        transport: str = "auto",
        server_path: Optional[str] = None,
        http_url: Optional[str] = None
    ) -> Union[MarcusClient, MarcusHttpClient]:
        """
        Create a Marcus client with the specified transport
        
        Parameters
        ----------
        transport : str
            Transport type: "stdio", "http", or "auto" (default)
        server_path : Optional[str]
            Path for stdio server (used with stdio transport)
        http_url : Optional[str]
            HTTP endpoint URL (used with HTTP transport)
        
        Returns
        -------
        Union[MarcusClient, MarcusHttpClient]
            Configured Marcus client
        """
        # Check environment for overrides
        env_transport = os.environ.get("MARCUS_TRANSPORT", transport)
        env_http_url = os.environ.get("MARCUS_HTTP_URL", http_url)
        
        if env_transport == "http":
            logger.info("Using HTTP transport for Marcus connection")
            return MarcusHttpClient(base_url=env_http_url)
            
        elif env_transport == "stdio":
            logger.info("Using stdio transport for Marcus connection")
            return MarcusClient(server_path=server_path)
            
        else:  # auto mode
            # Try HTTP first if URL is provided
            if env_http_url:
                logger.info("Auto mode: Trying HTTP transport first")
                return MarcusHttpClient(base_url=env_http_url)
            else:
                # Default to stdio for backward compatibility
                logger.info("Auto mode: Using stdio transport (no HTTP URL provided)")
                return MarcusClient(server_path=server_path)
    
    @staticmethod
    async def create_and_connect(
        transport: str = "auto",
        server_path: Optional[str] = None,
        http_url: Optional[str] = None,
        auto_discover: bool = True
    ) -> Optional[Union[MarcusClient, MarcusHttpClient]]:
        """
        Create and connect a Marcus client
        
        Parameters
        ----------
        transport : str
            Transport type: "stdio", "http", or "auto" (default)
        server_path : Optional[str]
            Path for stdio server
        http_url : Optional[str]
            HTTP endpoint URL
        auto_discover : bool
            Enable auto-discovery of Marcus instances
        
        Returns
        -------
        Optional[Union[MarcusClient, MarcusHttpClient]]
            Connected client or None if connection failed
        """
        client = MarcusClientFactory.create_client(transport, server_path, http_url)
        
        try:
            success = await client.connect(auto_discover=auto_discover)
            if success:
                return client
            else:
                logger.error(f"Failed to connect using {type(client).__name__}")
                # If auto mode and HTTP failed, try stdio
                if transport == "auto" and isinstance(client, MarcusHttpClient):
                    logger.info("Auto mode: HTTP failed, trying stdio transport")
                    stdio_client = MarcusClient(server_path=server_path)
                    if await stdio_client.connect(auto_discover=auto_discover):
                        return stdio_client
                return None
                
        except Exception as e:
            logger.error(f"Error connecting to Marcus: {e}")
            return None