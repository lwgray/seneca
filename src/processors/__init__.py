"""Data flow visualization system for Marcus"""

# Import the new local processor
from .conversation_processor import (
    ConversationProcessor,
    ConversationStreamProcessor as LocalConversationStreamProcessor,
    ConversationType
)

# Keep existing imports for compatibility
from .conversation_stream import ConversationStreamProcessor
from .ui_server import VisualizationServer

# Lazy imports to avoid loading NetworkX unless needed
def get_decision_visualizer():
    """Lazy import DecisionVisualizer to avoid NetworkX import"""
    from .decision_visualizer import DecisionVisualizer
    return DecisionVisualizer

def get_knowledge_graph_builder():
    """Lazy import KnowledgeGraphBuilder to avoid NetworkX import"""
    from .knowledge_graph import KnowledgeGraphBuilder
    return KnowledgeGraphBuilder

__all__ = [
    'ConversationProcessor',
    'ConversationStreamProcessor',
    'LocalConversationStreamProcessor',
    'ConversationType',
    'get_decision_visualizer', 
    'get_knowledge_graph_builder',
    'VisualizationServer'
]