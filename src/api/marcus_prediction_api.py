"""
Marcus Prediction API for Seneca.

This module provides API endpoints that interface with Marcus prediction tools
to expose AI intelligence capabilities for dashboard visualization.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, jsonify, request

from src.mcp_client.marcus_http_client import MarcusHTTPClient

logger = logging.getLogger(__name__)

# Create Blueprint
prediction_api = Blueprint("prediction_api", __name__, url_prefix="/api/predictions")

# Global client instance for reuse
_marcus_client: Optional[MarcusHTTPClient] = None


def get_marcus_client() -> MarcusHTTPClient:
    """Get configured Marcus HTTP client."""
    global _marcus_client
    if not _marcus_client:
        _marcus_client = MarcusHTTPClient(base_url="http://localhost:4300")
    return _marcus_client


@prediction_api.route("/project/<project_id>/completion", methods=["POST"])
def predict_project_completion(project_id: str):
    """
    Predict project completion time with confidence intervals.
    
    Returns predicted completion date, confidence intervals, velocity metrics,
    and risk factors for the specified project.
    """
    try:
        data = request.get_json() or {}
        include_confidence = data.get("include_confidence", request.args.get("include_confidence", "true").lower() == "true")
        
        client = get_marcus_client()
        
        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect to Marcus first
            connected = loop.run_until_complete(client.connect())
            if not connected:
                return jsonify({
                    "success": False,
                    "error": "Not connected to Marcus"
                }), 503
            
            # Authenticate as observer
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-predictions", "observer", "viewer")
            )
            
            if not auth_result.get("success"):
                logger.warning("Authentication failed, proceeding with limited access")
            
            # Call Marcus prediction tool
            result = loop.run_until_complete(
                client.call_tool("predict_completion_time", {
                    "project_id": project_id,
                    "include_confidence": include_confidence
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Prediction failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting completion for project {project_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@prediction_api.route("/task/<task_id>/outcome", methods=["POST"])
def predict_task_outcome(task_id: str):
    """
    Predict the outcome of a task assignment.
    
    Returns success probability, estimated duration, blockage risk,
    and confidence score for the task-agent pairing.
    """
    try:
        data = request.get_json() or {}
        agent_id = data.get("agent_id") or request.args.get("agent_id")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-predictions", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("predict_task_outcome", {
                    "task_id": task_id,
                    "agent_id": agent_id
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Task outcome prediction failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting outcome for task {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@prediction_api.route("/task/<task_id>/blockage-risk", methods=["POST"])
def predict_blockage_probability(task_id: str):
    """
    Predict the probability of a task becoming blocked.
    
    Returns blockage probability, likely causes, suggested mitigations,
    and dependencies at risk.
    """
    try:
        data = request.get_json() or {}
        include_mitigation = data.get("include_mitigation", request.args.get("include_mitigation", "true").lower() == "true")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-predictions", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("predict_blockage_probability", {
                    "task_id": task_id,
                    "include_mitigation": include_mitigation
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Blockage prediction failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting blockage for task {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@prediction_api.route("/task/<task_id>/cascade-effects", methods=["POST"])
def predict_cascade_effects(task_id: str):
    """
    Predict cascade effects if a task is delayed.
    
    Returns affected tasks, total delay impact, critical path changes,
    and project completion impact.
    """
    try:
        data = request.get_json() or {}
        delay_days = data.get("delay_days", int(request.args.get("delay_days", "1")))
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-predictions", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("predict_cascade_effects", {
                    "task_id": task_id,
                    "delay_days": delay_days
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Cascade effect prediction failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting cascade effects for task {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@prediction_api.route("/assignment/score", methods=["POST"])
def get_task_assignment_score():
    """
    Get assignment fitness score for agent-task pairing.
    
    Returns overall score, skill match, availability, historical performance,
    and assignment recommendation.
    """
    try:
        data = request.get_json() or {}
        task_id = data.get("task_id") or request.args.get("task_id")
        agent_id = data.get("agent_id") or request.args.get("agent_id")
        
        if not task_id or not agent_id:
            return jsonify({
                "success": False,
                "error": "Both task_id and agent_id are required"
            }), 400
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-predictions", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_task_assignment_score", {
                    "task_id": task_id,
                    "agent_id": agent_id
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Assignment scoring failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error scoring assignment {task_id} -> {agent_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@prediction_api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for prediction API."""
    try:
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Test Marcus connectivity
            ping_result = loop.run_until_complete(
                client.call_tool("ping", {"echo": "health-check"})
            )
        finally:
            loop.close()
        
        return jsonify({
            "status": "healthy",
            "marcus_connected": ping_result.get("success", False) if ping_result else False,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "marcus_connected": False,
            "timestamp": datetime.now().isoformat()
        })