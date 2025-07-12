"""
Conversation API endpoints for agent communication visualization

Provides real-time access to agent conversations, Marcus's decision-making process,
and communication analytics inspired by modern monitoring tools.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request
from flask_socketio import emit

# Use Seneca's local processors instead of Marcus imports
from ..processors.conversation_processor import (
    ConversationProcessor,
    ConversationStreamProcessor
)
# Import Seneca configuration
import sys
from pathlib import Path
# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import get_marcus_log_dir

# Create blueprint
conversation_api = Blueprint("conversation_api", __name__, url_prefix="/api/conversations")

# Get Marcus log directory from configuration
MARCUS_LOG_DIR = get_marcus_log_dir()

# Initialize components using local processors
try:
    conversation_processor = ConversationProcessor(MARCUS_LOG_DIR)
    stream_processor = ConversationStreamProcessor(MARCUS_LOG_DIR)
except ValueError as e:
    print(f"Warning: Could not initialize processors: {e}")
    # Create with a default path that might exist
    fallback_dir = Path(__file__).parent.parent.parent.parent / 'marcus' / 'logs' / 'conversations'
    if fallback_dir.exists():
        conversation_processor = ConversationProcessor(str(fallback_dir))
        stream_processor = ConversationStreamProcessor(str(fallback_dir))
    else:
        raise RuntimeError(f"Cannot find Marcus log directory. Please set MARCUS_LOG_DIR environment variable.")

# In-memory cache for recent conversations (in production, use Redis)
conversation_cache = []
MAX_CACHE_SIZE = 1000


@conversation_api.route("/recent", methods=["GET"])
def get_recent_conversations():
    """
    Get recent conversations with advanced filtering
    
    Query params:
    - agent_id: Filter by specific agent
    - task_id: Filter by task
    - type: Filter by conversation type (worker_message, pm_decision, etc.)
    - limit: Number of results (default 50, max 200)
    - offset: Pagination offset
    - time_range: Time range in minutes (default 60)
    """
    try:
        # Parse query parameters
        agent_id = request.args.get("agent_id")
        task_id = request.args.get("task_id")
        conv_type = request.args.get("type")
        limit = min(int(request.args.get("limit", 50)), 200)
        offset = int(request.args.get("offset", 0))
        time_range = int(request.args.get("time_range", 60))
        
        # Calculate time window
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_range)
        
        # Get conversations from processor
        conversations = conversation_processor.get_conversations_in_range(
            start_time=start_time,
            end_time=end_time,
            conversation_type=conv_type
        )
        
        # Apply filters
        if agent_id:
            conversations = [c for c in conversations if 
                           c.get("source") == agent_id or c.get("target") == agent_id]
        
        if task_id:
            conversations = [c for c in conversations if 
                           c.get("metadata", {}).get("task_id") == task_id]
        
        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        paginated = conversations[offset:offset + limit]
        
        # Calculate statistics
        stats = _calculate_conversation_stats(conversations)
        
        return jsonify({
            "success": True,
            "conversations": paginated,
            "total": len(conversations),
            "limit": limit,
            "offset": offset,
            "statistics": stats
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@conversation_api.route("/analytics", methods=["GET"])
def get_conversation_analytics():
    """
    Get conversation analytics and patterns
    
    Returns Grafana-style metrics for visualization
    """
    try:
        # Time range
        hours = int(request.args.get("hours", 24))
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get all conversations in range
        conversations = conversation_processor.get_conversations_in_range(
            start_time=start_time,
            end_time=end_time
        )
        
        # Calculate metrics
        metrics = {
            "message_volume": _calculate_message_volume(conversations),
            "agent_activity": _calculate_agent_activity(conversations),
            "decision_confidence": _calculate_decision_confidence(conversations),
            "response_times": _calculate_response_times(conversations),
            "blocker_frequency": _calculate_blocker_frequency(conversations),
            "task_flow": _calculate_task_flow(conversations)
        }
        
        return jsonify({
            "success": True,
            "analytics": metrics,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@conversation_api.route("/agent/<agent_id>/history", methods=["GET"])
def get_agent_conversation_history(agent_id: str):
    """Get conversation history for a specific agent"""
    try:
        limit = min(int(request.args.get("limit", 100)), 500)
        
        # Get agent-specific conversations
        conversations = conversation_processor.get_agent_conversations(agent_id, limit=limit)
        
        # Group by task
        grouped = _group_conversations_by_task(conversations)
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "conversations": conversations,
            "grouped_by_task": grouped,
            "total": len(conversations)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@conversation_api.route("/search", methods=["POST"])
def search_conversations():
    """
    Advanced search through conversations
    
    Supports full-text search, regex patterns, and semantic search
    """
    try:
        data = request.json
        query = data.get("query", "")
        search_type = data.get("type", "text")  # text, regex, semantic
        filters = data.get("filters", {})
        
        # Perform search based on type
        if search_type == "text":
            results = _text_search(query, filters)
        elif search_type == "regex":
            results = _regex_search(query, filters)
        elif search_type == "semantic":
            results = _semantic_search(query, filters)
        else:
            return jsonify({"success": False, "error": "Invalid search type"}), 400
        
        return jsonify({
            "success": True,
            "results": results,
            "query": query,
            "type": search_type
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@conversation_api.route("/stream/subscribe", methods=["POST"])
def subscribe_to_conversation_stream():
    """Subscribe to real-time conversation updates via WebSocket"""
    try:
        data = request.json
        filters = data.get("filters", {})
        
        # Store subscription filters in session
        session_id = request.headers.get("X-Session-ID", "default")
        
        # This would normally use Redis or similar
        # For now, we'll emit to all connected clients
        
        return jsonify({
            "success": True,
            "message": "Subscribed to conversation stream",
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Helper functions

def _calculate_conversation_stats(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics for conversations"""
    if not conversations:
        return {}
    
    # Count by type
    type_counts = {}
    for conv in conversations:
        conv_type = conv.get("type", "unknown")
        type_counts[conv_type] = type_counts.get(conv_type, 0) + 1
    
    # Average confidence for decisions
    decisions = [c for c in conversations if c.get("type") == "pm_decision"]
    avg_confidence = 0
    if decisions:
        confidences = [d.get("metadata", {}).get("confidence_score", 0) for d in decisions]
        avg_confidence = sum(confidences) / len(confidences)
    
    return {
        "total": len(conversations),
        "by_type": type_counts,
        "average_decision_confidence": avg_confidence,
        "unique_agents": len(set(c.get("source") for c in conversations if c.get("source")))
    }


def _calculate_message_volume(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate message volume over time (Grafana-style time series)"""
    # Group by hour
    hourly_counts = {}
    
    for conv in conversations:
        timestamp = conv.get("timestamp")
        if timestamp:
            hour = datetime.fromisoformat(timestamp).replace(minute=0, second=0, microsecond=0)
            hour_str = hour.isoformat()
            hourly_counts[hour_str] = hourly_counts.get(hour_str, 0) + 1
    
    # Convert to time series format
    series = [{"time": k, "value": v} for k, v in sorted(hourly_counts.items())]
    
    return {
        "series": series,
        "total": len(conversations),
        "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
    }


def _calculate_agent_activity(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate activity metrics per agent"""
    agent_metrics = {}
    
    for conv in conversations:
        source = conv.get("source")
        if source and source.startswith("agent"):
            if source not in agent_metrics:
                agent_metrics[source] = {
                    "messages_sent": 0,
                    "tasks_requested": 0,
                    "progress_reports": 0,
                    "blockers_reported": 0
                }
            
            agent_metrics[source]["messages_sent"] += 1
            
            conv_type = conv.get("type", "")
            if "request" in conv_type:
                agent_metrics[source]["tasks_requested"] += 1
            elif "progress" in conv_type:
                agent_metrics[source]["progress_reports"] += 1
            elif "blocker" in conv_type:
                agent_metrics[source]["blockers_reported"] += 1
    
    return agent_metrics


def _calculate_decision_confidence(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate decision confidence metrics"""
    decisions = [c for c in conversations if c.get("type") == "pm_decision"]
    
    if not decisions:
        return {"average": 0, "distribution": {}, "trend": []}
    
    # Confidence distribution
    distribution = {"high": 0, "medium": 0, "low": 0}
    confidence_values = []
    
    for decision in decisions:
        confidence = decision.get("metadata", {}).get("confidence_score", 0)
        confidence_values.append(confidence)
        
        if confidence >= 0.8:
            distribution["high"] += 1
        elif confidence >= 0.5:
            distribution["medium"] += 1
        else:
            distribution["low"] += 1
    
    # Time series of confidence
    trend = []
    for decision in sorted(decisions, key=lambda x: x.get("timestamp", "")):
        trend.append({
            "time": decision.get("timestamp"),
            "confidence": decision.get("metadata", {}).get("confidence_score", 0),
            "decision": decision.get("message", "")[:50]
        })
    
    return {
        "average": sum(confidence_values) / len(confidence_values),
        "distribution": distribution,
        "trend": trend
    }


def _calculate_response_times(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate response time metrics between requests and responses"""
    # This would need more sophisticated tracking of request-response pairs
    # For now, return placeholder data
    return {
        "average_ms": 1250,
        "p50_ms": 800,
        "p95_ms": 3000,
        "p99_ms": 5000
    }


def _calculate_blocker_frequency(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate blocker frequency and patterns"""
    blockers = [c for c in conversations if "blocker" in c.get("type", "").lower()]
    
    # Group by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    blocker_reasons = {}
    
    for blocker in blockers:
        severity = blocker.get("metadata", {}).get("severity", "medium")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Extract blocker reason (simplified)
        message = blocker.get("message", "")
        # This would use NLP in production
        reason = "technical" if any(word in message.lower() for word in ["error", "fail", "exception"]) else "other"
        blocker_reasons[reason] = blocker_reasons.get(reason, 0) + 1
    
    return {
        "total": len(blockers),
        "by_severity": severity_counts,
        "by_reason": blocker_reasons,
        "rate_per_hour": len(blockers) / 24 if conversations else 0
    }


def _calculate_task_flow(conversations: List[Dict]) -> Dict[str, Any]:
    """Calculate task flow metrics"""
    task_events = {}
    
    for conv in conversations:
        task_id = conv.get("metadata", {}).get("task_id")
        if task_id:
            if task_id not in task_events:
                task_events[task_id] = []
            task_events[task_id].append({
                "type": conv.get("type"),
                "timestamp": conv.get("timestamp"),
                "agent": conv.get("source")
            })
    
    # Calculate flow metrics
    completed_tasks = 0
    blocked_tasks = 0
    average_duration = 0
    
    for task_id, events in task_events.items():
        if any(e["type"] == "task_completed" for e in events):
            completed_tasks += 1
        if any("blocked" in e["type"] for e in events):
            blocked_tasks += 1
    
    return {
        "total_tasks": len(task_events),
        "completed": completed_tasks,
        "blocked": blocked_tasks,
        "completion_rate": completed_tasks / len(task_events) if task_events else 0
    }


def _group_conversations_by_task(conversations: List[Dict]) -> Dict[str, List[Dict]]:
    """Group conversations by task ID"""
    grouped = {}
    
    for conv in conversations:
        task_id = conv.get("metadata", {}).get("task_id", "no_task")
        if task_id not in grouped:
            grouped[task_id] = []
        grouped[task_id].append(conv)
    
    return grouped


def _text_search(query: str, filters: Dict) -> List[Dict]:
    """Perform text search through conversations"""
    # Simplified implementation
    results = []
    all_conversations = conversation_processor.get_recent_conversations(limit=1000)
    
    query_lower = query.lower()
    for conv in all_conversations:
        message = conv.get("message", "").lower()
        if query_lower in message:
            results.append(conv)
    
    return results[:100]  # Limit results


def _regex_search(pattern: str, filters: Dict) -> List[Dict]:
    """Perform regex search through conversations"""
    import re
    
    results = []
    all_conversations = conversation_processor.get_recent_conversations(limit=1000)
    
    try:
        regex = re.compile(pattern)
        for conv in all_conversations:
            message = conv.get("message", "")
            if regex.search(message):
                results.append(conv)
    except re.error:
        return []
    
    return results[:100]


def _semantic_search(query: str, filters: Dict) -> List[Dict]:
    """Perform semantic search through conversations"""
    # This would use embeddings in production
    # For now, fallback to text search
    return _text_search(query, filters)