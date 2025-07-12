"""
Mock AI Analysis Engine for Seneca.

This module provides a simplified AI analysis engine that doesn't require
Marcus dependencies. In a real deployment, this could be replaced with
actual AI integration.
"""

import asyncio
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import ProjectState, RiskLevel, TaskStatus, WorkerStatus


class AIAnalysisEngine:
    """
    Mock AI analysis engine for project health monitoring.
    
    This is a simplified version that provides reasonable mock data
    for visualization purposes without requiring actual AI backends.
    """
    
    def __init__(self):
        """Initialize the mock AI engine."""
        self.initialized = False
        self._analysis_count = 0
    
    async def initialize(self):
        """Initialize the AI engine (mock implementation)."""
        await asyncio.sleep(0.1)  # Simulate initialization
        self.initialized = True
    
    async def analyze_project_health(
        self,
        project_state: ProjectState,
        recent_activities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze project health and return insights.
        
        Args:
            project_state: Current state of the project
            recent_activities: Recent conversation activities
            
        Returns:
            Dictionary containing health analysis results
        """
        if not self.initialized:
            await self.initialize()
        
        self._analysis_count += 1
        
        # Calculate basic health metrics
        health_score = self._calculate_health_score(project_state)
        risk_level = self._determine_risk_level(health_score)
        
        # Generate insights based on project state
        insights = self._generate_insights(project_state, recent_activities)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(project_state, risk_level)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "risk_level": risk_level.value,
            "insights": insights,
            "recommendations": recommendations,
            "metrics": {
                "total_tasks": project_state.total_tasks,
                "completed_tasks": project_state.completed_tasks,
                "blocked_tasks": project_state.blocked_tasks,
                "active_workers": project_state.active_workers,
                "completion_percentage": project_state.completion_percentage,
                "velocity": self._calculate_velocity(recent_activities),
                "blocker_rate": self._calculate_blocker_rate(project_state)
            },
            "analysis_id": f"analysis_{self._analysis_count}"
        }
    
    def _calculate_health_score(self, project_state: ProjectState) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        # Deduct for blocked tasks
        if project_state.total_tasks > 0:
            blocker_ratio = project_state.blocked_tasks / project_state.total_tasks
            score -= blocker_ratio * 30
        
        # Deduct for idle workers
        idle_workers = len([w for w in project_state.workers if w.status == WorkerStatus.IDLE])
        if project_state.workers:
            idle_ratio = idle_workers / len(project_state.workers)
            score -= idle_ratio * 20
        
        # Boost for good completion rate
        if project_state.completion_percentage > 70:
            score = min(score + 10, 100)
        
        return max(0, min(score, 100))
    
    def _determine_risk_level(self, health_score: float) -> RiskLevel:
        """Determine risk level based on health score."""
        if health_score >= 80:
            return RiskLevel.LOW
        elif health_score >= 60:
            return RiskLevel.MEDIUM
        elif health_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_insights(
        self,
        project_state: ProjectState,
        recent_activities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights about the project."""
        insights = []
        
        # Task-based insights
        if project_state.blocked_tasks > 2:
            insights.append(f"{project_state.blocked_tasks} tasks are currently blocked")
        
        if project_state.completion_percentage > 80:
            insights.append("Project is nearing completion")
        elif project_state.completion_percentage < 20:
            insights.append("Project is in early stages")
        
        # Worker-based insights
        idle_count = len([w for w in project_state.workers if w.status == WorkerStatus.IDLE])
        if idle_count > 0:
            insights.append(f"{idle_count} workers are idle and available for tasks")
        
        # Activity-based insights
        if recent_activities:
            blocker_activities = [
                a for a in recent_activities 
                if a.get("type", "").lower().endswith("blocker")
            ]
            if len(blocker_activities) > 3:
                insights.append("High number of blockers reported recently")
        
        return insights
    
    def _generate_recommendations(
        self,
        project_state: ProjectState,
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate recommendations based on project state."""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Prioritize resolving blocked tasks")
        
        idle_workers = [w for w in project_state.workers if w.status == WorkerStatus.IDLE]
        if idle_workers and project_state.total_tasks > project_state.completed_tasks:
            recommendations.append("Assign idle workers to pending tasks")
        
        if project_state.blocked_tasks > 0:
            recommendations.append("Review and address task dependencies")
        
        return recommendations
    
    def _calculate_velocity(self, recent_activities: List[Dict[str, Any]]) -> float:
        """Calculate activity velocity (messages per hour)."""
        if not recent_activities:
            return 0.0
        
        # Mock calculation - in reality would analyze timestamps
        return random.uniform(5.0, 20.0)
    
    def _calculate_blocker_rate(self, project_state: ProjectState) -> float:
        """Calculate blocker rate as percentage."""
        if project_state.total_tasks == 0:
            return 0.0
        
        return (project_state.blocked_tasks / project_state.total_tasks) * 100