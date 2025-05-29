"""
Experiment model definitions.
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    INTERRUPTED = "interrupted"


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
            data={"current": current, "total": total, "percentage": current / total * 100}
        )
    
    @classmethod
    def metric(cls, name: str, value: Any) -> "ExperimentLog":
        """Create a metric log entry."""
        return cls(
            type=LogType.METRIC,
            message=f"Metric: {name} = {value}",
            data={"name": name, "value": value}
        )
    
    @classmethod
    def artifact(cls, name: str, path: Path) -> "ExperimentLog":
        """Create an artifact log entry."""
        return cls(
            type=LogType.ARTIFACT,
            message=f"Artifact saved: {name} at {path}",
            data={"name": name, "path": path}
        )
    
    @classmethod
    def error(cls, message: str, error_details: Optional[str] = None) -> "ExperimentLog":
        """Create an error log entry."""
        return cls(
            type=LogType.ERROR,
            message=message,
            data={"error_details": error_details} if error_details else {}
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
            data={"resource_type": resource_type, "usage": usage}
        )
    
    @classmethod
    def config(cls, key: str, value: Any) -> "ExperimentLog":
        """Create a config log entry."""
        return cls(
            type=LogType.CONFIG,
            message=f"Config: {key} = {value}",
            data={"key": key, "value": value}
        )
    
    @classmethod
    def tag(cls, tag: str) -> "ExperimentLog":
        """Create a tag log entry."""
        return cls(
            type=LogType.TAG,
            message=f"Tag added: {tag}",
            data={"tag": tag}
        )


class Experiment(BaseModel):
    """
    Model representing an experiment.
    """
    id: str
    name: str
    logs: List[ExperimentLog] = Field(default_factory=list)
    
    @property
    def status(self) -> ExperimentStatus:
        """Get the current status of the experiment."""
        # Check for error logs
        for log in reversed(self.logs):
            if log.type == LogType.ERROR:
                return ExperimentStatus.ERROR
        
        # Check for end logs
        for log in reversed(self.logs):
            if log.type == LogType.END:
                if "interrupted" in log.message.lower():
                    return ExperimentStatus.INTERRUPTED
                return ExperimentStatus.COMPLETED
        
        # If no end or error logs, the experiment is running
        return ExperimentStatus.RUNNING
    
    @property
    def start_time(self) -> datetime:
        """Get the start time of the experiment."""
        for log in self.logs:
            if log.type == LogType.START:
                return log.timestamp
        # If no start log, use the timestamp of the first log
        return self.logs[0].timestamp if self.logs else datetime.now()
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Get the end time of the experiment."""
        for log in reversed(self.logs):
            if log.type == LogType.END or log.type == LogType.ERROR:
                return log.timestamp
        return None
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the experiment in seconds."""
        if self.end_time is None:
            if self.status == ExperimentStatus.RUNNING:
                # For running experiments, calculate duration up to now
                return (datetime.now() - self.start_time).total_seconds()
            return None
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration of the experiment."""
        config = {}
        for log in self.logs:
            if log.type == LogType.CONFIG:
                config[log.data["key"]] = log.data["value"]
        return config
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get the metrics of the experiment."""
        metrics = {}
        for log in self.logs:
            if log.type == LogType.METRIC:
                metrics[log.data["name"]] = log.data["value"]
        return metrics
    
    @property
    def artifacts(self) -> Dict[str, Path]:
        """Get the artifacts of the experiment."""
        artifacts = {}
        for log in self.logs:
            if log.type == LogType.ARTIFACT:
                artifacts[log.data["name"]] = log.data["path"]
        return artifacts
    
    @property
    def error(self) -> Optional[str]:
        """Get the error message of the experiment."""
        for log in reversed(self.logs):
            if log.type == LogType.ERROR:
                return log.message
        return None
    
    @property
    def tags(self) -> List[str]:
        """Get the tags of the experiment."""
        tags = []
        for log in self.logs:
            if log.type == LogType.TAG:
                tag = log.data["tag"]
                if tag not in tags:
                    tags.append(tag)
        return tags
    
    @property
    def progress(self) -> Optional[Dict[str, Any]]:
        """Get the latest progress of the experiment."""
        for log in reversed(self.logs):
            if log.type == LogType.PROGRESS:
                return log.data
        return None
    
    def add_log(self, log: ExperimentLog) -> None:
        """Add a log entry to the experiment."""
        self.logs.append(log)
    
    def start(self, message: str = "Experiment started") -> None:
        """Mark the experiment as started."""
        self.add_log(ExperimentLog.start(message))
    
    def complete(self) -> None:
        """Mark the experiment as completed."""
        self.add_log(ExperimentLog.end("Experiment completed"))
    
    def fail(self, error_message: str, details: Optional[str] = None) -> None:
        """Mark the experiment as failed with an error message."""
        self.add_log(ExperimentLog.error(error_message, details))
        self.add_log(ExperimentLog.end("Experiment failed"))
    
    def interrupt(self) -> None:
        """Mark the experiment as interrupted."""
        self.add_log(ExperimentLog.end("Experiment interrupted"))
    
    def set_metric(self, name: str, value: Any) -> None:
        """Set a metric for the experiment."""
        self.add_log(ExperimentLog.metric(name, value))
    
    def add_artifact(self, name: str, path: Path) -> None:
        """Add an artifact to the experiment."""
        self.add_log(ExperimentLog.artifact(name, path))
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the experiment."""
        if tag not in self.tags:
            self.add_log(ExperimentLog.tag(tag))
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration parameter for the experiment."""
        self.add_log(ExperimentLog.config(key, value))
    
    def update_progress(self, current: int, total: int, message: str = "") -> None:
        """Update the progress of the experiment."""
        self.add_log(ExperimentLog.progress(current, total, message))
    
    def log_info(self, message: str) -> None:
        """Log an informational message."""
        self.add_log(ExperimentLog.info(message))
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.add_log(ExperimentLog.warning(message))
    
    def log_resource(self, resource_type: str, usage: Any) -> None:
        """Log resource usage."""
        self.add_log(ExperimentLog.resource(resource_type, usage))


class ExperimentList(BaseModel):
    """
    Model representing a list of experiments.
    """
    experiments: Dict[str, Experiment] = Field(default_factory=dict)
    
    def add(self, experiment: Experiment) -> None:
        """Add an experiment to the list."""
        self.experiments[experiment.id] = experiment
    
    def get(self, experiment_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        return self.experiments.get(experiment_id)
    
    def remove(self, experiment_id: str) -> None:
        """Remove an experiment from the list."""
        if experiment_id in self.experiments:
            del self.experiments[experiment_id]
    
    def filter(self, 
               status: Optional[Union[ExperimentStatus, List[ExperimentStatus]]] = None,
               tags: Optional[List[str]] = None) -> "ExperimentList":
        """
        Filter experiments by status and/or tags.
        
        Args:
            status: Status or list of statuses to filter by
            tags: List of tags to filter by (experiments must have all tags)
            
        Returns:
            A new ExperimentList with filtered experiments
        """
        filtered = ExperimentList()
        
        # Convert single status to list for consistent handling
        status_list = [status] if isinstance(status, ExperimentStatus) else status
        
        for exp_id, exp in self.experiments.items():
            # Check status filter
            if status_list and exp.status not in status_list:
                continue
                
            # Check tags filter (all specified tags must be present)
            if tags and not all(tag in exp.tags for tag in tags):
                continue
                
            filtered.add(exp)
            
        return filtered
    
    def sort_by(self, key: str, reverse: bool = False) -> List[Experiment]:
        """
        Sort experiments by a specific attribute.
        
        Args:
            key: Attribute to sort by (e.g., 'start_time', 'name')
            reverse: Whether to sort in descending order
            
        Returns:
            Sorted list of experiments
        """
        return sorted(
            self.experiments.values(),
            key=lambda exp: getattr(exp, key, None),
            reverse=reverse
        )
    
    @property
    def running(self) -> "ExperimentList":
        """Get all running experiments."""
        return self.filter(status=ExperimentStatus.RUNNING)
    
    @property
    def completed(self) -> "ExperimentList":
        """Get all completed experiments."""
        return self.filter(status=ExperimentStatus.COMPLETED)
    
    @property
    def failed(self) -> "ExperimentList":
        """Get all failed experiments."""
        return self.filter(status=ExperimentStatus.ERROR)
    
    @property
    def count(self) -> int:
        """Get the number of experiments."""
        return len(self.experiments)