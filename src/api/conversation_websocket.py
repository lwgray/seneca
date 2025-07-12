"""
WebSocket handlers for real-time conversation streaming
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Set

from flask import request
from flask_socketio import emit, join_room, leave_room

from src.logging.conversation_logger import ConversationLogger
from src.visualization.conversation_stream import ConversationStreamProcessor


# Track connected clients and their subscriptions
connected_clients: Set[str] = set()
client_filters: Dict[str, Dict[str, Any]] = {}

# Initialize components
conversation_logger = ConversationLogger()
stream_processor = ConversationStreamProcessor(conversation_logger.log_dir)

# Logger
logger = logging.getLogger(__name__)


def setup_conversation_websocket_handlers(socketio):
    """
    Setup WebSocket handlers for conversation streaming
    
    Parameters
    ----------
    socketio : SocketIO
        Flask-SocketIO instance
    """
    
    @socketio.on('connect', namespace='/conversations')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid
        connected_clients.add(client_id)
        join_room(client_id)
        
        logger.info(f"Client connected: {client_id}")
        emit('connected', {'client_id': client_id})
        
        # Send initial agent list
        emit_active_agents()
    
    @socketio.on('disconnect', namespace='/conversations')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid
        connected_clients.discard(client_id)
        client_filters.pop(client_id, None)
        leave_room(client_id)
        
        logger.info(f"Client disconnected: {client_id}")
    
    @socketio.on('subscribe', namespace='/conversations')
    def handle_subscribe(data):
        """Handle conversation stream subscription"""
        client_id = request.sid
        filters = data.get('filters', {})
        
        # Store client filters
        client_filters[client_id] = filters
        
        logger.info(f"Client {client_id} subscribed with filters: {filters}")
        emit('subscribed', {'status': 'success', 'filters': filters})
    
    @socketio.on('unsubscribe', namespace='/conversations')
    def handle_unsubscribe():
        """Handle conversation stream unsubscription"""
        client_id = request.sid
        client_filters.pop(client_id, None)
        
        logger.info(f"Client {client_id} unsubscribed")
        emit('unsubscribed', {'status': 'success'})
    
    def emit_active_agents():
        """Emit list of active agents to all clients"""
        # Get unique agents from recent conversations
        recent_conversations = conversation_logger.get_recent_conversations(limit=500)
        agents = set()
        
        for conv in recent_conversations:
            source = conv.get('source', '')
            target = conv.get('target', '')
            
            if source.startswith(('agent', 'worker')):
                agents.add(source)
            if target.startswith(('agent', 'worker')):
                agents.add(target)
        
        agent_list = [
            {'id': agent, 'name': agent.replace('_', ' ').title()}
            for agent in sorted(agents)
        ]
        
        emit('agents_update', {'agents': agent_list}, namespace='/conversations', broadcast=True)
    
    def handle_new_conversation(event):
        """
        Handle new conversation event from stream processor
        
        Parameters
        ----------
        event : ConversationEvent
            New conversation event
        """
        # Convert event to dict
        event_data = event.to_dict()
        
        # Emit to all connected clients based on their filters
        for client_id, filters in client_filters.items():
            if should_emit_to_client(event_data, filters):
                emit('conversation', event_data, room=client_id, namespace='/conversations')
        
        # Check if this is a PM thinking event
        if event.event_type == 'pm_thinking':
            emit('marcus_thinking', {
                'thought': event.message,
                'timestamp': event.timestamp.isoformat()
            }, namespace='/conversations', broadcast=True)
    
    def should_emit_to_client(event: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if event should be emitted to client based on filters
        
        Parameters
        ----------
        event : Dict[str, Any]
            Event data
        filters : Dict[str, Any]
            Client filters
            
        Returns
        -------
        bool
            True if event should be emitted
        """
        # Check agent filter
        agent_filter = filters.get('agentId')
        if agent_filter:
            if event.get('source') != agent_filter and event.get('target') != agent_filter:
                return False
        
        # Check type filters
        type_filters = filters.get('types', {})
        event_type = event.get('event_type', event.get('type', 'unknown'))
        
        # Map event types to filter keys
        type_mapping = {
            'worker_message': 'worker_message',
            'pm_decision': 'pm_decision',
            'pm_thinking': 'pm_thinking',
            'blocker_report': 'blocker',
            'blocker': 'blocker'
        }
        
        filter_key = type_mapping.get(event_type, event_type)
        if filter_key in type_filters and not type_filters[filter_key]:
            return False
        
        return True
    
    # Register event handler with stream processor
    stream_processor.add_event_handler(handle_new_conversation)
    
    # Return a function to start the streaming
    async def start_conversation_streaming():
        """Start the conversation streaming process"""
        try:
            await stream_processor.start_streaming()
        except Exception as e:
            logger.error(f"Error in conversation streaming: {e}")
    
    return start_conversation_streaming


def emit_conversation_update(conversation_data: Dict[str, Any]):
    """
    Emit a conversation update to all connected clients
    
    This can be called from other parts of the system to push
    real-time updates to the UI.
    
    Parameters
    ----------
    conversation_data : Dict[str, Any]
        Conversation data to emit
    """
    from flask_socketio import emit
    
    # Add timestamp if not present
    if 'timestamp' not in conversation_data:
        conversation_data['timestamp'] = datetime.now().isoformat()
    
    # Emit to all clients based on their filters
    for client_id, filters in client_filters.items():
        if should_emit_to_client(conversation_data, filters):
            emit('conversation', conversation_data, room=client_id, namespace='/conversations')