"""
Log model definitions for experiments.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LogType(str, Enum):
    """Type of log entry."""

    START = "start"
    END = "end"
    PROGRESS = "progress"
    METRIC = "metric"
    ARTIFACT = "artifact"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    RESOURCE = "resource"
    CONFIG = "config"
    TAG = "tag"


class ExperimentLog(BaseModel):
    """
    Log entry for an experiment.
    """

    timestamp: datetime = Field(default_factory=datetime.now)
    type: LogType
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def start(cls, message: str = "Experiment started") -> "ExperimentLog":
        """Create a start log entry."""
        return cls(type=LogType.START, message=message)

    @classmethod
    def end(cls, message: str = "Experiment completed") -> "ExperimentLog":
        """Create an end log entry."""
        return cls(type=LogType.END, message=message)

    @classmethod
    def progress(cls, current: int, total: int, message: str = "") -> "ExperimentLog":
        """Create a progress log entry."""
        return cls(
            type=LogType.PROGRESS,
            message=message or f"Progress: {current}/{total}",
            data={
                "current": current,
                "total": total,
                "percentage": current / total * 100,
            },
        )

    @classmethod
    def metric(cls, name: str, value: Any) -> "ExperimentLog":
        """Create a metric log entry."""
        return cls(
            type=LogType.METRIC,
            message=f"Metric: {name} = {value}",
            data={"name": name, "value": value},
        )

    @classmethod
    def artifact(cls, name: str, path: Path) -> "ExperimentLog":
        """Create an artifact log entry."""
        return cls(
            type=LogType.ARTIFACT,
            message=f"Artifact saved: {name} at {path}",
            data={"name": name, "path": path},
        )

    @classmethod
    def error(
        cls, message: str, error_details: Optional[str] = None
    ) -> "ExperimentLog":
        """Create an error log entry."""
        return cls(
            type=LogType.ERROR,
            message=message,
            data={"error_details": error_details} if error_details else {},
        )

    @classmethod
    def info(cls, message: str) -> "ExperimentLog":
        """Create an info log entry."""
        return cls(type=LogType.INFO, message=message)

    @classmethod
    def warning(cls, message: str) -> "ExperimentLog":
        """Create a warning log entry."""
        return cls(type=LogType.WARNING, message=message)

    @classmethod
    def resource(cls, resource_type: str, usage: Any) -> "ExperimentLog":
        """Create a resource usage log entry."""
        return cls(
            type=LogType.RESOURCE,
            message=f"Resource usage: {resource_type} = {usage}",
            data={"resource_type": resource_type, "usage": usage},
        )

    @classmethod
    def config(cls, key: str, value: Any) -> "ExperimentLog":
        """Create a config log entry."""
        return cls(
            type=LogType.CONFIG,
            message=f"Config: {key} = {value}",
            data={"key": key, "value": value},
        )

    @classmethod
    def tag(cls, tag: str) -> "ExperimentLog":
        """Create a tag log entry."""
        return cls(type=LogType.TAG, message=f"Tag added: {tag}", data={"tag": tag})