"""
Conversation stream processing for real-time Marcus analytics.

This module processes conversation events from Marcus and streams them
to the Seneca frontend for real-time visualization.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationStreamProcessor:
    """
    Processes and streams conversation events from Marcus to Seneca frontend.
    
    Handles real-time conversation data, filters events, and formats them
    for dashboard visualization.
    """
    
    def __init__(self, marcus_client=None):
        """Initialize the conversation stream processor."""
        self.marcus_client = marcus_client
        self.active_streams = set()
        self.event_filters = {}
        
    async def start_stream(self, client_id: str, filters: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
        """
        Start streaming conversation events to a client.
        
        Args:
            client_id: Unique identifier for the client connection
            filters: Optional filters for conversation events
            
        Yields:
            Formatted conversation events as JSON strings
        """
        try:
            self.active_streams.add(client_id)
            self.event_filters[client_id] = filters or {}
            
            # Mock conversation events for now
            # In production, this would connect to Marcus event streams
            while client_id in self.active_streams:
                event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "conversation_update",
                    "data": {
                        "agent_id": "test-agent",
                        "message": "Processing task...",
                        "status": "active"
                    }
                }
                
                if self._should_include_event(event, filters):
                    yield json.dumps(event)
                
                await asyncio.sleep(1)  # Stream every second
                
        except Exception as e:
            logger.error(f"Error in conversation stream for {client_id}: {e}")
        finally:
            self.stop_stream(client_id)
    
    def stop_stream(self, client_id: str):
        """Stop streaming for a specific client."""
        self.active_streams.discard(client_id)
        self.event_filters.pop(client_id, None)
        
    def _should_include_event(self, event: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        """Check if an event should be included based on filters."""
        if not filters:
            return True
            
        # Apply basic filtering logic
        if "agent_id" in filters and event.get("data", {}).get("agent_id") != filters["agent_id"]:
            return False
            
        if "event_type" in filters and event.get("type") != filters["event_type"]:
            return False
            
        return True