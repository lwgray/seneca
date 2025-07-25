"""
Project workflow management for coordinating Marcus tasks.

This module manages project workflows by interfacing with Marcus
through the MCP client to orchestrate multi-step development tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProjectWorkflowManager:
    """
    Manages project workflows and coordinates with Marcus.
    
    Handles workflow creation, execution, and status tracking
    by interfacing with Marcus through MCP client.
    """
    
    def __init__(self, marcus_client=None):
        """Initialize the workflow manager."""
        self.marcus_client = marcus_client
        self.active_workflows = {}
        self.workflow_history = []
        
    async def start_workflow(self, project_id: str, workflow_type: str, **kwargs) -> Dict[str, Any]:
        """
        Start a new project workflow.
        
        Args:
            project_id: ID of the project
            workflow_type: Type of workflow to start
            **kwargs: Additional workflow parameters
            
        Returns:
            Workflow status and information
        """
        try:
            workflow_id = f"{project_id}_{workflow_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            workflow = {
                "id": workflow_id,
                "project_id": project_id,
                "type": workflow_type,
                "status": "started",
                "started_at": datetime.utcnow().isoformat(),
                "parameters": kwargs,
                "steps": []
            }
            
            self.active_workflows[workflow_id] = workflow
            logger.info(f"Started workflow {workflow_id} for project {project_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": "started",
                "message": f"Workflow {workflow_type} started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def pause_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Pause an active workflow.
        
        Args:
            workflow_id: ID of the workflow to pause
            
        Returns:
            Pause operation result
        """
        try:
            if workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "paused"
            workflow["paused_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Paused workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": "paused",
                "message": "Workflow paused successfully"
            }
            
        except Exception as e:
            logger.error(f"Error pausing workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Stop an active workflow.
        
        Args:
            workflow_id: ID of the workflow to stop
            
        Returns:
            Stop operation result
        """
        try:
            if workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": "Workflow not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "stopped"
            workflow["stopped_at"] = datetime.utcnow().isoformat()
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Stopped workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": "stopped",
                "message": "Workflow stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow status information or None if not found
        """
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        
        # Check history
        for workflow in self.workflow_history:
            if workflow["id"] == workflow_id:
                return workflow
                
        return None
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """
        List all active workflows.
        
        Returns:
            List of active workflow information
        """
        return list(self.active_workflows.values())