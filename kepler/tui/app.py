"""
Terminal UI for experiment management.
"""

from pathlib import Path
from textual.app import App
from textual.widgets import Footer, Header
from textual.widgets import ContentSwitcher, Static
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from kepler.models import (
    get_experiments_file_path,
    load_experiments,
)


class ExperimentFileHandler(FileSystemEventHandler):
    """
    File system event handler for experiment file changes.
    """

    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if (
            not event.is_directory
            and Path(event.src_path) == get_experiments_file_path()
        ):
            self.callback()


class ExperimentMonitor:
    """
    Monitor for experiment file changes.
    """

    def __init__(self, callback):
        self.callback = callback
        self.observer = Observer()
        self.handler = ExperimentFileHandler(callback)
        self.path = get_experiments_file_path().parent

    def start(self):
        """Start monitoring for changes."""
        self.observer.schedule(self.handler, self.path, recursive=False)
        self.observer.start()

    def stop(self):
        """Stop monitoring for changes."""
        self.observer.stop()
        self.observer.join()


class ExperimentTUI(App):
    """
    Terminal UI for experiment management.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)

        # Create a monitor for experiment file changes
        self.monitor = ExperimentMonitor(self.refresh_experiments)

        # Load initial experiments
        self.experiments = load_experiments()

        # Filter state
        self.show_running_only = False

        # Currently selected experiment for logs view
        self.selected_experiment_id = None

        # Current view (experiments or logs)
        self.current_view = "experiments"

    def on_mount(self) -> None:
        """Mount the application."""
        # Set up the UI
        self.bind("q", "quit")
        self.bind("r", "refresh")
        self.bind("f", "toggle_filter")
        self.bind("b", "back_to_experiments")
        self.bind("l", "toggle_logs_view")

        # Start the monitor
        self.monitor.start()

        # Render the experiments
        self.render_experiments()

    def compose(self):
        """Compose the application."""
        # Create the UI components
        yield Header()
        self.content = ContentSwitcher(id="content")
        yield self.content
        yield Footer()

    async def action_refresh(self) -> None:
        """Refresh the experiments."""
        self.refresh_experiments()

    async def action_toggle_filter(self) -> None:
        """Toggle the filter for running experiments."""
        self.show_running_only = not self.show_running_only
        self.render_experiments()

    async def action_back_to_experiments(self) -> None:
        """Go back to the experiments view."""
        if self.current_view != "experiments":
            self.current_view = "experiments"
            self.render_experiments()

    async def action_toggle_logs_view(self) -> None:
        """Toggle between experiments and logs view."""
        if self.current_view == "experiments":
            # If we have a selected experiment, show its logs
            if self.selected_experiment_id:
                self.current_view = "logs"
                self.render_logs(self.selected_experiment_id)
        else:
            # Go back to experiments view
            self.current_view = "experiments"
            self.render_experiments()

    # We're now using keyboard shortcuts instead of buttons

    def refresh_experiments(self) -> None:
        """Refresh the experiments from disk."""
        self.experiments = load_experiments()
        if self.current_view == "experiments":
            self.render_experiments()
        elif self.current_view == "logs" and self.selected_experiment_id:
            self.render_logs(self.selected_experiment_id)

    def render_experiments(self) -> None:
        """Render the experiments in the UI."""
        # Filter experiments if needed
        if self.show_running_only:
            filtered_experiments = self.experiments.running
            filter_status = "Showing running experiments only"
        else:
            filtered_experiments = self.experiments
            filter_status = "Showing all experiments"

        # Create a simple text representation
        lines = [f"Experiments ({filtered_experiments.count}) - {filter_status}", ""]

        # Header
        lines.append(
            "ID                      Name                Status              Start Time           Duration    Tags"
        )
        lines.append("-" * 100)

        # Get sorted experiments
        experiments = filtered_experiments.sort_by("start_time", reverse=True)

        # Add rows for each experiment
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

            # Format status
            status_str = str(exp.status)

            # Format tags
            tags_str = ", ".join(exp.tags) if exp.tags else ""

            # Format the row
            lines.append(
                f"{exp.id:<24} {exp.name:<20} {status_str:<20} {exp.start_time.strftime('%Y-%m-%d %H:%M:%S'):<20} {duration_str:<10} {tags_str}"
            )

            # Add a line to indicate how to view logs
            lines.append("  Press L to view logs (select experiment first)")
            lines.append("")

        # Add summary information
        lines.extend(
            [
                "",
                "Summary:",
                f"Total: {self.experiments.count}",
                f"Running: {self.experiments.running.count}",
                f"Completed: {self.experiments.completed.count}",
                f"Failed: {self.experiments.failed.count}",
                "",
                "Press F to toggle filter",
                "Press L to view logs of selected experiment",
                "Press R to refresh",
                "Press Q to quit",
            ]
        )

        # Create a new content widget
        content = Static("\n".join(lines), id="experiments")

        # Update the content
        if "experiments" in self.content.children:
            self.content.remove_child(self.content.get_child_by_id("experiments"))

        self.content.mount(content)
        self.content.current = "experiments"

        # Set the first experiment as selected if none is selected
        if not self.selected_experiment_id and experiments:
            self.selected_experiment_id = experiments[0].id

    def render_logs(self, experiment_id: str) -> None:
        """Render the logs for a specific experiment."""
        # Get the experiment
        exp = self.experiments.get(experiment_id)
        if not exp:
            # If experiment not found, go back to experiments view
            self.current_view = "experiments"
            self.render_experiments()
            return

        # Create a simple text representation
        lines = [f"Logs for Experiment: {exp.name} ({exp.id})", ""]

        # Header
        lines.append("Timestamp                Type       Message")
        lines.append("-" * 100)

        # Add rows for each log entry
        for log in exp.logs:
            # Format the row
            lines.append(
                f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  {log.type.value:<10} {log.message}"
            )

            # Add data details if present
            if log.data:
                for key, value in log.data.items():
                    lines.append(f"  {key}: {value}")

        # Add navigation information
        lines.extend(
            [
                "",
                "Press B to go back to experiments view",
                "Press R to refresh",
                "Press Q to quit",
            ]
        )

        # Create a new content widget
        content = Static("\n".join(lines), id="logs")

        # Update the content
        if "logs" in self.content.children:
            self.content.remove_child(self.content.get_child_by_id("logs"))
        self.content.mount(content)
        self.content.current = "logs"

    async def action_quit(self) -> None:
        """Quit the application."""
        # Stop the monitor
        self.monitor.stop()

        # Exit the application
        self.exit()


def run_tui():
    """Run the terminal UI."""
    app = ExperimentTUI()
    app.run()
