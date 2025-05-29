"""
Storage functionality for experiment data.
"""
import json
import os
from pathlib import Path
from typing import Optional

import click

from kepler.models.experiment import ExperimentList


def get_app_dir() -> Path:
    """
    Get the application directory for storing experiment data.
    Uses click's app directory functionality.
    
    Returns:
        Path to the application directory
    """
    app_dir = Path(click.get_app_dir("expman"))
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_experiments_file_path() -> Path:
    """
    Get the path to the experiments file.
    
    Returns:
        Path to the experiments file
    """
    return get_app_dir() / "experiments.json"


def save_experiments(experiment_list: ExperimentList) -> None:
    """
    Save the experiment list to disk.
    
    Args:
        experiment_list: The experiment list to save
    """
    file_path = get_experiments_file_path()
    with open(file_path, "w") as f:
        f.write(experiment_list.model_dump_json(indent=2))


def load_experiments() -> ExperimentList:
    """
    Load the experiment list from disk.
    
    Returns:
        The loaded experiment list, or a new one if the file doesn't exist
    """
    file_path = get_experiments_file_path()
    
    if not file_path.exists():
        return ExperimentList()
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return ExperimentList.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        # Handle corrupted file
        # In a real application, we might want to create a backup
        # of the corrupted file before creating a new one
        click.echo(f"Error loading experiments file: {e}", err=True)
        return ExperimentList()


def get_experiment_dir(experiment_id: str) -> Path:
    """
    Get the directory for storing experiment artifacts.
    
    Args:
        experiment_id: ID of the experiment
        
    Returns:
        Path to the experiment directory
    """
    exp_dir = get_app_dir() / "experiments" / experiment_id
    os.makedirs(exp_dir, exist_ok=True)
    return exp_dir