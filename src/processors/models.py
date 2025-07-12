"""
Local models for Seneca processors.

This module provides model definitions that were previously imported from Marcus.
These are simplified versions focused on what Seneca needs for visualization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Status of a task in the project."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class WorkerStatus(Enum):
    """Status of a worker/agent."""
    IDLE = "idle"
    WORKING = "working"
    BLOCKED = "blocked"
    OFFLINE = "offline"


class RiskLevel(Enum):
    """Risk level for project health."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Represents a task in the project."""
    id: str
    title: str
    status: TaskStatus
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Worker:
    """Represents a worker/agent in the system."""
    id: str
    name: str
    status: WorkerStatus
    current_task: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectState:
    """Current state of the project."""
    name: str
    tasks: List[Task]
    workers: List[Worker]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_tasks(self) -> int:
        """Total number of tasks in the project."""
        return len(self.tasks)
    
    @property
    def completed_tasks(self) -> int:
        """Number of completed tasks."""
        return len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
    
    @property
    def blocked_tasks(self) -> int:
        """Number of blocked tasks."""
        return len([t for t in self.tasks if t.status == TaskStatus.BLOCKED])
    
    @property
    def active_workers(self) -> int:
        """Number of active workers."""
        return len([w for w in self.workers if w.status == WorkerStatus.WORKING])
    
    @property
    def completion_percentage(self) -> float:
        """Percentage of tasks completed."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100