# Kepler - Experiment Management Tool

Kepler is a Python package for managing, tracking, and monitoring experiments. It provides tools for defining experiment configurations, saving results, and monitoring progress through a terminal user interface (TUI).

## Features

- Define experiments with metadata using Pydantic models
- Log-based experiment tracking with detailed history
- Track experiment status (running, completed, error)
- Save and load experiment data to/from disk
- Utilities for saving Pydantic models and Pandas DataFrames
- Terminal UI for monitoring experiment progress and viewing logs
- CLI for managing experiments

## Installation

```bash
pip install kepler
```

## Quick Start

### Define and run an experiment

```python
from kepler.api import experiment, save_dataframe
import pandas as pd

# Define and run an experiment
with experiment("my_experiment", {"learning_rate": 0.01, "batch_size": 32}) as exp:
    # Log some information
    exp.log_info("Starting training process")
    
    # Your experiment code here
    for epoch in range(10):
        # Update progress
        exp.update_progress(epoch + 1, 10, f"Processing epoch {epoch + 1}/10")
        
        # Log metrics
        exp.set_metric(f"accuracy_epoch_{epoch+1}", 0.85 + 0.01 * epoch)
        exp.set_metric(f"loss_epoch_{epoch+1}", 0.35 - 0.01 * epoch)
        
        # Log resource usage
        exp.log_resource("memory", "250MB")
    
    # Save results
    results = pd.DataFrame({"accuracy": [0.85, 0.87, 0.90], "loss": [0.35, 0.30, 0.25]})
    df_path = save_dataframe(results, "training_metrics")
    exp.log_info(f"Saved training metrics to {df_path}")
    
    # Set final metrics
    exp.set_metric("final_accuracy", 0.90)
    exp.set_metric("final_loss", 0.25)
```

### Examples

Check out the examples directory for more detailed examples:
- `basic_experiment.py`: A simple example of using Kepler for experiment tracking
- `multiple_experiments.py`: Running multiple experiments with different configurations
- `kepler_notebook_example.ipynb`: Using Kepler in a Jupyter notebook environment

### Monitor experiments

Run the TUI to monitor your experiments:

```bash
kepler tui
```

## Log-Based Experiment Model

Kepler uses a log-based approach for tracking experiments:

- Each experiment contains a chronological list of log entries
- Log types include: START, END, PROGRESS, METRIC, ARTIFACT, ERROR, INFO, WARNING, RESOURCE, CONFIG, TAG
- Experiment properties (status, metrics, config, etc.) are computed from the logs
- This provides a complete history of the experiment's execution

### Available Log Methods

```python
# Basic logging
exp.log_info("Informational message")
exp.log_warning("Warning message")

# Progress tracking
exp.update_progress(current=5, total=10, message="Processing batch 5/10")

# Configuration and metrics
exp.set_config("learning_rate", 0.01)
exp.set_metric("accuracy", 0.95)

# Resource usage
exp.log_resource("gpu_memory", "2.5GB")

# Tags
exp.add_tag("production")
```

## CLI Commands

- `kepler tui`: Launch the terminal UI for monitoring experiments
- `kepler list`: List all experiments
- `kepler info <experiment_id>`: Show detailed information about an experiment
- `kepler clean`: Clean up old or failed experiments

## License

MIT