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
    message: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


class StartLog(BaseLog):
    """Log entry for experiment start."""
    kind: Literal[LogKind.START] = LogKind.START
    message: str = "Experiment started"


class EndLog(BaseLog):
    """Log entry for experiment end."""
    kind: Literal[LogKind.END] = LogKind.END
    message: str = "Experiment completed"


class ProgressLog(BaseLog):
    """Log entry for experiment progress."""
    kind: Literal[LogKind.PROGRESS] = LogKind.PROGRESS
    current: int
    total: int
    message: str = ""
    
    @property
    def percentage(self) -> float:
        """Calculate the progress percentage."""
        return self.current / self.total * 100
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set default message if not provided
        if not self.message:
            self.message = f"Progress: {self.current}/{self.total}"
        
        # Update data with progress information
        self.data.update({
            "current": self.current,
            "total": self.total,
            "percentage": self.percentage,
        })


class MetricLog(BaseLog):
    """Log entry for experiment metrics."""
    kind: Literal[LogKind.METRIC] = LogKind.METRIC
    name: str
    value: Any
    message: str = ""  # Default empty message that will be set in post_init
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set message based on name and value if not provided
        if not self.message:
            self.message = f"Metric: {self.name} = {self.value}"
        
        # Update data with metric information
        self.data.update({
            "name": self.name,
            "value": self.value,
        })


class ArtifactLog(BaseLog):
    """Log entry for experiment artifacts."""
    kind: Literal[LogKind.ARTIFACT] = LogKind.ARTIFACT
    name: str
    path: Path
    message: str = ""  # Default empty message that will be set in post_init
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set message based on name and path if not provided
        if not self.message:
            self.message = f"Artifact saved: {self.name} at {self.path}"
        
        # Update data with artifact information
        self.data.update({
            "name": self.name,
            "path": self.path,
        })


class ErrorLog(BaseLog):
    """Log entry for experiment errors."""
    kind: Literal[LogKind.ERROR] = LogKind.ERROR
    error_details: Optional[str] = None
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Update data with error details if provided
        if self.error_details:
            self.data.update({"error_details": self.error_details})


class InfoLog(BaseLog):
    """Log entry for experiment information."""
    kind: Literal[LogKind.INFO] = LogKind.INFO


class WarningLog(BaseLog):
    """Log entry for experiment warnings."""
    kind: Literal[LogKind.WARNING] = LogKind.WARNING


class ResourceLog(BaseLog):
    """Log entry for experiment resource usage."""
    kind: Literal[LogKind.RESOURCE] = LogKind.RESOURCE
    resource_type: str
    usage: Any
    message: str = ""  # Default empty message that will be set in post_init
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set message based on resource type and usage if not provided
        if not self.message:
            self.message = f"Resource usage: {self.resource_type} = {self.usage}"
        
        # Update data with resource information
        self.data.update({
            "resource_type": self.resource_type,
            "usage": self.usage,
        })


class ConfigLog(BaseLog):
    """Log entry for experiment configuration."""
    kind: Literal[LogKind.CONFIG] = LogKind.CONFIG
    key: str
    value: Any
    message: str = ""  # Default empty message that will be set in post_init
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set message based on key and value if not provided
        if not self.message:
            self.message = f"Config: {self.key} = {self.value}"
        
        # Update data with config information
        self.data.update({
            "key": self.key,
            "value": self.value,
        })


class TagLog(BaseLog):
    """Log entry for experiment tags."""
    kind: Literal[LogKind.TAG] = LogKind.TAG
    tag: str
    message: str = ""  # Default empty message that will be set in post_init
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Set message based on tag if not provided
        if not self.message:
            self.message = f"Tag added: {self.tag}"
        
        # Update data with tag information
        self.data.update({"tag": self.tag})


# For backward compatibility
class ExperimentLog(BaseLog):
    """
    Legacy log entry for an experiment.
    
    This class is maintained for backward compatibility.
    New code should use the specific log classes instead.
    """
    # Required field for BaseLog, but will be set by factory methods
    kind: LogKind = LogKind.INFO
    
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