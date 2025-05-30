"""
Log model definitions for experiments.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class LogKind(str, Enum):
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


class BaseLog(BaseModel):
    """
    Base log entry for an experiment.
    """
    created_at: datetime = Field(default_factory=datetime.now)
    kind: LogKind
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class StartLog(BaseLog):
    """Log entry for experiment start."""
    kind: Literal[LogKind.START] = LogKind.START
    
    def __init__(self, message: str = "Experiment started", **kwargs):
        super().__init__(message=message, **kwargs)


class EndLog(BaseLog):
    """Log entry for experiment end."""
    kind: Literal[LogKind.END] = LogKind.END
    
    def __init__(self, message: str = "Experiment completed", **kwargs):
        super().__init__(message=message, **kwargs)


class ProgressLog(BaseLog):
    """Log entry for experiment progress."""
    kind: Literal[LogKind.PROGRESS] = LogKind.PROGRESS
    
    def __init__(self, current: int, total: int, message: str = "", **kwargs):
        data = {
            "current": current,
            "total": total,
            "percentage": current / total * 100,
        }
        super().__init__(
            message=message or f"Progress: {current}/{total}",
            data=data,
            **kwargs
        )


class MetricLog(BaseLog):
    """Log entry for experiment metrics."""
    kind: Literal[LogKind.METRIC] = LogKind.METRIC
    
    def __init__(self, name: str, value: Any, **kwargs):
        data = {"name": name, "value": value}
        super().__init__(
            message=f"Metric: {name} = {value}",
            data=data,
            **kwargs
        )


class ArtifactLog(BaseLog):
    """Log entry for experiment artifacts."""
    kind: Literal[LogKind.ARTIFACT] = LogKind.ARTIFACT
    
    def __init__(self, name: str, path: Path, **kwargs):
        data = {"name": name, "path": path}
        super().__init__(
            message=f"Artifact saved: {name} at {path}",
            data=data,
            **kwargs
        )


class ErrorLog(BaseLog):
    """Log entry for experiment errors."""
    kind: Literal[LogKind.ERROR] = LogKind.ERROR
    
    def __init__(self, message: str, error_details: Optional[str] = None, **kwargs):
        data = {"error_details": error_details} if error_details else {}
        super().__init__(message=message, data=data, **kwargs)


class InfoLog(BaseLog):
    """Log entry for experiment information."""
    kind: Literal[LogKind.INFO] = LogKind.INFO
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)


class WarningLog(BaseLog):
    """Log entry for experiment warnings."""
    kind: Literal[LogKind.WARNING] = LogKind.WARNING
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)


class ResourceLog(BaseLog):
    """Log entry for experiment resource usage."""
    kind: Literal[LogKind.RESOURCE] = LogKind.RESOURCE
    
    def __init__(self, resource_type: str, usage: Any, **kwargs):
        data = {"resource_type": resource_type, "usage": usage}
        super().__init__(
            message=f"Resource usage: {resource_type} = {usage}",
            data=data,
            **kwargs
        )


class ConfigLog(BaseLog):
    """Log entry for experiment configuration."""
    kind: Literal[LogKind.CONFIG] = LogKind.CONFIG
    
    def __init__(self, key: str, value: Any, **kwargs):
        data = {"key": key, "value": value}
        super().__init__(
            message=f"Config: {key} = {value}",
            data=data,
            **kwargs
        )


class TagLog(BaseLog):
    """Log entry for experiment tags."""
    kind: Literal[LogKind.TAG] = LogKind.TAG
    
    def __init__(self, tag: str, **kwargs):
        data = {"tag": tag}
        super().__init__(
            message=f"Tag added: {tag}",
            data=data,
            **kwargs
        )


# For backward compatibility
class ExperimentLog(BaseLog):
    """
    Legacy log entry for an experiment.
    
    This class is maintained for backward compatibility.
    New code should use the specific log classes instead.
    """
    
    # Alias timestamp to created_at for backward compatibility
    @property
    def timestamp(self) -> datetime:
        return self.created_at
    
    # Alias type to kind for backward compatibility
    @property
    def type(self) -> LogKind:
        return self.kind
    
    @classmethod
    def start(cls, message: str = "Experiment started") -> StartLog:
        """Create a start log entry."""
        return StartLog(message=message)

    @classmethod
    def end(cls, message: str = "Experiment completed") -> EndLog:
        """Create an end log entry."""
        return EndLog(message=message)

    @classmethod
    def progress(cls, current: int, total: int, message: str = "") -> ProgressLog:
        """Create a progress log entry."""
        return ProgressLog(current=current, total=total, message=message)

    @classmethod
    def metric(cls, name: str, value: Any) -> MetricLog:
        """Create a metric log entry."""
        return MetricLog(name=name, value=value)

    @classmethod
    def artifact(cls, name: str, path: Path) -> ArtifactLog:
        """Create an artifact log entry."""
        return ArtifactLog(name=name, path=path)

    @classmethod
    def error(cls, message: str, error_details: Optional[str] = None) -> ErrorLog:
        """Create an error log entry."""
        return ErrorLog(message=message, error_details=error_details)

    @classmethod
    def info(cls, message: str) -> InfoLog:
        """Create an info log entry."""
        return InfoLog(message=message)

    @classmethod
    def warning(cls, message: str) -> WarningLog:
        """Create a warning log entry."""
        return WarningLog(message=message)

    @classmethod
    def resource(cls, resource_type: str, usage: Any) -> ResourceLog:
        """Create a resource usage log entry."""
        return ResourceLog(resource_type=resource_type, usage=usage)

    @classmethod
    def config(cls, key: str, value: Any) -> ConfigLog:
        """Create a config log entry."""
        return ConfigLog(key=key, value=value)

    @classmethod
    def tag(cls, tag: str) -> TagLog:
        """Create a tag log entry."""
        return TagLog(tag=tag)