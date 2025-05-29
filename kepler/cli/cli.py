"""
Command-line interface for experiment management.
"""

from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table

from kepler.api import delete_experiment, get_experiment, get_experiments
from kepler.models import ExperimentStatus, get_app_dir
from kepler.tui.app import run_tui


@click.group()
@click.version_option()
def cli():
    """Experiment management tool."""
    pass


@cli.command()
def tui():
    """Launch the terminal UI for monitoring experiments."""
    run_tui()


@cli.command()
@click.option(
    "--status",
    "-s",
    type=click.Choice(["running", "completed", "error", "interrupted"]),
    help="Filter by status",
)
@click.option(
    "--tag", "-t", multiple=True, help="Filter by tag (can be used multiple times)"
)
@click.option(
    "--sort",
    type=click.Choice(["name", "start_time", "end_time", "status"]),
    default="start_time",
    help="Sort by field",
)
@click.option("--reverse/--no-reverse", default=True, help="Reverse sort order")
def list(status: Optional[str], tag: List[str], sort: str, reverse: bool):
    """List experiments."""
    console = Console()

    # Load experiments
    experiment_list = get_experiments()

    # Filter by status if provided
    if status:
        experiment_list = experiment_list.filter(status=ExperimentStatus(status))

    # Filter by tags if provided
    if tag:
        experiment_list = experiment_list.filter(tags=list(tag))

    # Sort experiments
    experiments = experiment_list.sort_by(sort, reverse=reverse)

    if not experiments:
        console.print("[yellow]No experiments found.[/yellow]")
        return

    # Create a table
    table = Table(title="Experiments")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status", style="bold")
    table.add_column("Start Time")
    table.add_column("Duration")
    table.add_column("Tags")

    # Add rows
    for exp in experiments:
        # Format duration
        duration = exp.duration
        if duration is not None:
            if duration < 60:
                duration_str = f"{duration:.1f}s"
            elif duration < 3600:
                duration_str = f"{duration / 60:.1f}m"
            else:
                duration_str = f"{duration / 3600:.1f}h"
        else:
            duration_str = "N/A"

        # Format status with color
        status_colors = {
            ExperimentStatus.RUNNING: "blue",
            ExperimentStatus.COMPLETED: "green",
            ExperimentStatus.ERROR: "red",
            ExperimentStatus.INTERRUPTED: "yellow",
        }
        status_str = (
            f"[{status_colors[exp.status]}]{exp.status}[/{status_colors[exp.status]}]"
        )

        # Format tags
        tags_str = ", ".join(exp.tags) if exp.tags else ""

        table.add_row(
            exp.id,
            exp.name,
            status_str,
            exp.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration_str,
            tags_str,
        )

    console.print(table)


@cli.command()
@click.argument("experiment_id")
def info(experiment_id: str):
    """Show detailed information about an experiment."""
    console = Console()

    # Get the experiment
    exp = get_experiment(experiment_id)

    if not exp:
        console.print(f"[red]Experiment with ID '{experiment_id}' not found.[/red]")
        return

    # Print experiment details
    console.print(f"[bold cyan]Experiment: {exp.name} ({exp.id})[/bold cyan]")
    console.print(f"Status: [bold]{exp.status}[/bold]")
    console.print(f"Start Time: {exp.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if exp.end_time:
        console.print(f"End Time: {exp.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    if exp.duration is not None:
        console.print(f"Duration: {exp.duration:.2f} seconds")

    if exp.tags:
        console.print(f"Tags: {', '.join(exp.tags)}")

    if exp.error:
        console.print(f"Error: [red]{exp.error}[/red]")

    # Print configuration
    if exp.config:
        console.print("\n[bold]Configuration:[/bold]")
        for key, value in exp.config.items():
            console.print(f"  {key}: {value}")

    # Print metrics
    if exp.metrics:
        console.print("\n[bold]Metrics:[/bold]")
        for key, value in exp.metrics.items():
            console.print(f"  {key}: {value}")

    # Print artifacts
    if exp.artifacts:
        console.print("\n[bold]Artifacts:[/bold]")
        for name, path in exp.artifacts.items():
            console.print(f"  {name}: {path}")


@cli.command()
@click.argument("experiment_id")
@click.option(
    "--force/--no-force", default=False, help="Force deletion without confirmation"
)
def delete(experiment_id: str, force: bool):
    """Delete an experiment and its artifacts."""
    console = Console()

    # Get the experiment
    exp = get_experiment(experiment_id)

    if not exp:
        console.print(f"[red]Experiment with ID '{experiment_id}' not found.[/red]")
        return

    # Confirm deletion
    if not force and not click.confirm(
        f"Are you sure you want to delete experiment '{exp.name}' ({exp.id})?"
    ):
        console.print("Deletion cancelled.")
        return

    # Delete the experiment
    if delete_experiment(experiment_id):
        console.print(
            f"[green]Experiment '{exp.name}' ({exp.id}) deleted successfully.[/green]"
        )
    else:
        console.print(
            f"[red]Failed to delete experiment '{exp.name}' ({exp.id}).[/red]"
        )


@cli.command()
def dir():
    """Show the application directory."""
    console = Console()
    app_dir = get_app_dir()
    console.print(f"Application directory: [bold]{app_dir}[/bold]")

    # Check if the directory exists
    if not app_dir.exists():
        console.print(
            "[yellow]Directory does not exist yet. It will be created when you run your first experiment.[/yellow]"
        )
        return

    # List contents
    console.print("\nContents:")
    for item in app_dir.iterdir():
        if item.is_file():
            console.print(f"  [cyan]{item.name}[/cyan] ({item.stat().st_size} bytes)")
        elif item.is_dir():
            console.print(f"  [blue]{item.name}/[/blue] (directory)")


if __name__ == "__main__":
    cli()
