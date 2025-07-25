"""
Marcus Analytics API for Seneca.

This module provides API endpoints that interface with Marcus analytics tools
to collect metrics and performance data for dashboard visualization.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, jsonify, request

from src.mcp_client.marcus_http_client import MarcusHTTPClient

logger = logging.getLogger(__name__)

# Create Blueprint
analytics_api = Blueprint("analytics_api", __name__, url_prefix="/api/analytics")

# Global client instance for reuse
_marcus_client: Optional[MarcusHTTPClient] = None


def get_marcus_client() -> MarcusHTTPClient:
    """Get configured Marcus HTTP client."""
    global _marcus_client
    if not _marcus_client:
        _marcus_client = MarcusHTTPClient(base_url="http://localhost:4298")
    return _marcus_client


@analytics_api.route("/system/metrics", methods=["GET"])
def get_system_metrics():
    """
    Get system-wide performance metrics.
    
    Returns active agents, throughput, average task duration,
    and overall system health score.
    """
    try:
        time_window = request.args.get("time_window", "24h")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_system_metrics", {
                    "time_window": time_window
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "System metrics retrieval failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/agent/<agent_id>/metrics", methods=["GET"])
def get_agent_metrics(agent_id: str):
    """
    Get performance metrics for a specific agent.
    
    Returns utilization, tasks completed, success rate, average task time,
    and skill distribution for the agent.
    """
    try:
        time_window = request.args.get("time_window", "7d")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_agent_metrics", {
                    "agent_id": agent_id,
                    "time_window": time_window
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", f"Agent metrics for {agent_id} failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting agent metrics for {agent_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/project/<project_id>/metrics", methods=["GET"])
def get_project_metrics(project_id: str):
    """
    Get comprehensive project metrics.
    
    Returns velocity, progress percentage, health score,
    and burndown chart data for the project.
    """
    try:
        time_window = request.args.get("time_window", "7d")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_project_metrics", {
                    "project_id": project_id,
                    "time_window": time_window
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", f"Project metrics for {project_id} failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting project metrics for {project_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/tasks/metrics", methods=["GET"])
def get_task_metrics():
    """
    Get aggregated task metrics.
    
    Returns task counts, completion rates, blockage rates,
    and average hours grouped by the specified field.
    """
    try:
        time_window = request.args.get("time_window", "30d")
        group_by = request.args.get("group_by", "status")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_task_metrics", {
                    "time_window": time_window,
                    "group_by": group_by
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Task metrics retrieval failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting task metrics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/code/<agent_id>/metrics", methods=["GET"])
def get_code_metrics(agent_id: str):
    """
    Get code production metrics for an agent.
    
    Returns commits, lines added/deleted, files changed,
    language distribution, and PR statistics.
    """
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_code_metrics", {
                    "agent_id": agent_id,
                    "start_date": start_date,
                    "end_date": end_date
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", f"Code metrics for {agent_id} failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting code metrics for {agent_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/repository/<repository>/metrics", methods=["GET"])
def get_repository_metrics(repository: str):
    """
    Get repository-wide code metrics.
    
    Returns commit frequency, active contributors, PR statistics,
    and language breakdown for the repository.
    """
    try:
        time_window = request.args.get("time_window", "7d")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_repository_metrics", {
                    "repository": repository,
                    "time_window": time_window
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", f"Repository metrics for {repository} failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting repository metrics for {repository}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/code-review/metrics", methods=["GET"])
def get_code_review_metrics():
    """
    Get code review activity metrics.
    
    Returns review participation, turnaround times, approval rates,
    and review bottlenecks.
    """
    try:
        agent_id = request.args.get("agent_id")
        time_window = request.args.get("time_window", "7d")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_code_review_metrics", {
                    "agent_id": agent_id,
                    "time_window": time_window
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "Code review metrics failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting code review metrics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/code-quality/<repository>/metrics", methods=["GET"])
def get_code_quality_metrics(repository: str):
    """
    Get code quality metrics from static analysis.
    
    Returns coverage, complexity, technical debt, security issues,
    and quality gate status.
    """
    try:
        branch = request.args.get("branch", "main")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-analytics", "observer", "viewer")
            )
            
            result = loop.run_until_complete(
                client.call_tool("get_code_quality_metrics", {
                    "repository": repository,
                    "branch": branch
                })
            )
        finally:
            loop.close()
        
        if not result or not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", f"Code quality metrics for {repository} failed") if result else "No result from Marcus"
            }), 400
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting code quality metrics for {repository}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_api.route("/dashboard/overview", methods=["GET"])
def get_dashboard_overview():
    """
    Get comprehensive dashboard overview data.
    
    Combines system metrics, project metrics, and predictions
    into a single response for efficient dashboard loading.
    """
    try:
        project_id = request.args.get("project_id")
        time_window = request.args.get("time_window", "7d")
        
        client = get_marcus_client()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auth_result = loop.run_until_complete(
                client.authenticate("seneca-dashboard", "observer", "viewer")
            )
            
            # Fetch multiple metrics in parallel would be ideal,
            # but for now we'll fetch sequentially
            
            # System metrics
            system_result = loop.run_until_complete(
                client.call_tool("get_system_metrics", {
                    "time_window": time_window
                })
            )
            
            # Project metrics (if project_id provided)
            project_result = None
            if project_id:
                project_result = loop.run_until_complete(
                    client.call_tool("get_project_metrics", {
                        "project_id": project_id,
                        "time_window": time_window
                    })
                )
            
            # Task breakdown
            task_result = loop.run_until_complete(
                client.call_tool("get_task_metrics", {
                    "time_window": time_window,
                    "group_by": "status"
                })
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "data": {
                "system_metrics": system_result if system_result and system_result.get("success") else None,
                "project_metrics": project_result if project_result and project_result.get("success") else None,
                "task_breakdown": task_result if task_result and task_result.get("success") else None,
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return jsonify({"success": False, "error": str(e)}), 500