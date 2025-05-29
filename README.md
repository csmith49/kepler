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

```python
from kepler.api import experiment, save_dataframe
import pandas as pd

# Define and run an experiment
with experiment("my_experiment", {"learning_rate": 0.01, "batch_size": 32}) as exp:
    # Log some information
    exp.log_info("Starting training process")
    
    # Your experiment code here
    for epoch in range(5):
        # Update progress
        exp.update_progress(epoch + 1, 5, f"Processing epoch {epoch + 1}/5")
        
        # Log metrics
        exp.set_metric(f"accuracy", 0.85 + 0.03 * epoch)
        
    # Set final metrics
    exp.set_metric("final_accuracy", 0.95)
```

## Examples

Check out the [examples directory](./examples) for more detailed examples:
- `basic_experiment.py`: A simple example of using Kepler for experiment tracking
- `multiple_experiments.py`: Running multiple experiments with different configurations
- `kepler_notebook_example.ipynb`: Using Kepler in a Jupyter notebook environment

See the [Examples README](./examples/README.md) for more information.

## CLI Commands

- `kepler tui`: Launch the terminal UI for monitoring experiments
- `kepler list`: List all experiments
- `kepler info <experiment_id>`: Show detailed information about an experiment
- `kepler clean`: Clean up old or failed experiments

## License

MIT