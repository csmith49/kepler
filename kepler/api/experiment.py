"""
API for experiment management.
"""
import contextlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union

import pandas as pd
from pydantic import BaseModel

from kepler.models import (
    Experiment,
    ExperimentList,
    ExperimentStatus,
    get_experiment_dir,
    load_experiments,
    save_experiments,
)


@contextlib.contextmanager
def experiment(
    name: str,
    config: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
    id: Optional[str] = None,
) -> Generator[Experiment, None, None]:
    """
    Context manager for running an experiment.
    
    Args:
        name: Name of the experiment
        config: Configuration parameters for the experiment
        tags: Tags for categorizing the experiment
        id: Optional ID for the experiment (generated if not provided)
        
    Yields:
        The experiment object
    """
    # Generate a unique ID if not provided
    experiment_id = id or f"{name}-{uuid.uuid4().hex[:8]}"
    
    # Create the experiment
    exp = Experiment(
        id=experiment_id,
        name=name,
    )
    
    # Start the experiment
    exp.start(f"Starting experiment: {name}")
    
    # Add configuration if provided
    if config:
        for key, value in config.items():
            exp.set_config(key, value)
    
    # Add tags if provided
    if tags:
        for tag in tags:
            exp.add_tag(tag)
    
    # Load existing experiments
    experiment_list = load_experiments()
    
    # Add the new experiment
    experiment_list.add(exp)
    
    # Save the updated list
    save_experiments(experiment_list)
    
    try:
        # Yield the experiment to the caller
        yield exp
        
        # Mark as completed if no exceptions occurred
        exp.complete()
    except Exception as e:
        # Mark as failed if an exception occurred
        exp.fail(str(e))
        raise
    finally:
        # Update the experiment in the list
        experiment_list = load_experiments()
        experiment_list.add(exp)
        save_experiments(experiment_list)


def save_model(model: BaseModel, name: str, experiment_id: Optional[str] = None) -> Path:
    """
    Save a Pydantic model to disk.
    
    Args:
        model: The Pydantic model to save
        name: Name to give the saved model
        experiment_id: ID of the experiment (uses the most recent running experiment if not provided)
        
    Returns:
        Path to the saved model file
    """
    # Get the experiment ID if not provided
    if experiment_id is None:
        experiment_list = load_experiments()
        running_exps = experiment_list.running.sort_by("start_time", reverse=True)
        if not running_exps:
            raise ValueError("No running experiments found")
        experiment_id = running_exps[0].id
    
    # Get the experiment directory
    exp_dir = get_experiment_dir(experiment_id)
    
    # Create the file path
    file_path = exp_dir / f"{name}.json"
    
    # Save the model
    with open(file_path, "w") as f:
        f.write(model.model_dump_json(indent=2))
    
    # Update the experiment's artifacts
    experiment_list = load_experiments()
    exp = experiment_list.get(experiment_id)
    if exp:
        exp.add_artifact(name, file_path)
        experiment_list.add(exp)
        save_experiments(experiment_list)
    
    return file_path


def save_dataframe(
    df: pd.DataFrame, name: str, experiment_id: Optional[str] = None, format: str = "csv"
) -> Path:
    """
    Save a pandas DataFrame to disk.
    
    Args:
        df: The DataFrame to save
        name: Name to give the saved DataFrame
        experiment_id: ID of the experiment (uses the most recent running experiment if not provided)
        format: Format to save the DataFrame in ("csv" or "parquet")
        
    Returns:
        Path to the saved DataFrame file
    """
    # Get the experiment ID if not provided
    if experiment_id is None:
        experiment_list = load_experiments()
        running_exps = experiment_list.running.sort_by("start_time", reverse=True)
        if not running_exps:
            raise ValueError("No running experiments found")
        experiment_id = running_exps[0].id
    
    # Get the experiment directory
    exp_dir = get_experiment_dir(experiment_id)
    
    # Create the file path based on the format
    if format.lower() == "csv":
        file_path = exp_dir / f"{name}.csv"
        df.to_csv(file_path, index=False)
    elif format.lower() == "parquet":
        file_path = exp_dir / f"{name}.parquet"
        df.to_parquet(file_path, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    # Update the experiment's artifacts
    experiment_list = load_experiments()
    exp = experiment_list.get(experiment_id)
    if exp:
        exp.add_artifact(name, file_path)
        experiment_list.add(exp)
        save_experiments(experiment_list)
    
    return file_path


def save_dict(
    data: Dict[str, Any], name: str, experiment_id: Optional[str] = None
) -> Path:
    """
    Save a dictionary to disk as JSON.
    
    Args:
        data: The dictionary to save
        name: Name to give the saved dictionary
        experiment_id: ID of the experiment (uses the most recent running experiment if not provided)
        
    Returns:
        Path to the saved JSON file
    """
    # Get the experiment ID if not provided
    if experiment_id is None:
        experiment_list = load_experiments()
        running_exps = experiment_list.running.sort_by("start_time", reverse=True)
        if not running_exps:
            raise ValueError("No running experiments found")
        experiment_id = running_exps[0].id
    
    # Get the experiment directory
    exp_dir = get_experiment_dir(experiment_id)
    
    # Create the file path
    file_path = exp_dir / f"{name}.json"
    
    # Save the dictionary
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    # Update the experiment's artifacts
    experiment_list = load_experiments()
    exp = experiment_list.get(experiment_id)
    if exp:
        exp.add_artifact(name, file_path)
        experiment_list.add(exp)
        save_experiments(experiment_list)
    
    return file_path


def get_experiment(experiment_id: str) -> Optional[Experiment]:
    """
    Get an experiment by ID.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        The experiment, or None if not found
    """
    experiment_list = load_experiments()
    return experiment_list.get(experiment_id)


def get_experiments() -> ExperimentList:
    """
    Get all experiments.
    
    Returns:
        List of all experiments
    """
    return load_experiments()


def delete_experiment(experiment_id: str) -> bool:
    """
    Delete an experiment and its artifacts.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        True if the experiment was deleted, False otherwise
    """
    experiment_list = load_experiments()
    exp = experiment_list.get(experiment_id)
    
    if not exp:
        return False
    
    # Remove the experiment from the list
    experiment_list.remove(experiment_id)
    save_experiments(experiment_list)
    
    # Delete the experiment directory
    exp_dir = get_experiment_dir(experiment_id)
    if exp_dir.exists():
        import shutil
        shutil.rmtree(exp_dir)
    
    return True