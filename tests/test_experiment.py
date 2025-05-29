"""
Tests for the experiment model and API.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from kepler.api import experiment, save_dict, save_model
from kepler.models import Experiment, ExperimentList, ExperimentStatus, load_experiments


class TestExperiment:
    """Tests for the Experiment model."""
    
    def test_experiment_creation(self):
        """Test creating an experiment."""
        exp = Experiment(id="test-123", name="Test Experiment")
        
        assert exp.id == "test-123"
        assert exp.name == "Test Experiment"
        assert exp.status == ExperimentStatus.RUNNING
        assert exp.config == {}
        assert exp.metrics == {}
        assert exp.artifacts == {}
        assert exp.tags == []
        assert exp.error is None
        assert exp.end_time is None
    
    def test_experiment_completion(self):
        """Test completing an experiment."""
        exp = Experiment(id="test-123", name="Test Experiment")
        exp.complete()
        
        assert exp.status == ExperimentStatus.COMPLETED
        assert exp.end_time is not None
    
    def test_experiment_failure(self):
        """Test failing an experiment."""
        exp = Experiment(id="test-123", name="Test Experiment")
        exp.fail("Something went wrong")
        
        assert exp.status == ExperimentStatus.ERROR
        assert exp.error == "Something went wrong"
        assert exp.end_time is not None
    
    def test_experiment_metrics(self):
        """Test setting metrics."""
        exp = Experiment(id="test-123", name="Test Experiment")
        exp.set_metric("accuracy", 0.95)
        exp.set_metric("loss", 0.05)
        
        assert exp.metrics["accuracy"] == 0.95
        assert exp.metrics["loss"] == 0.05
    
    def test_experiment_duration(self):
        """Test experiment duration calculation."""
        exp = Experiment(id="test-123", name="Test Experiment")
        
        # Duration for running experiment
        assert exp.duration is not None
        assert exp.duration >= 0
        
        # Duration for completed experiment
        exp.complete()
        assert exp.duration is not None
        assert exp.duration >= 0


class TestExperimentList:
    """Tests for the ExperimentList model."""
    
    def test_add_experiment(self):
        """Test adding an experiment to the list."""
        exp_list = ExperimentList()
        exp = Experiment(id="test-123", name="Test Experiment")
        
        exp_list.add(exp)
        
        assert exp_list.count == 1
        assert exp_list.get("test-123") == exp
    
    def test_remove_experiment(self):
        """Test removing an experiment from the list."""
        exp_list = ExperimentList()
        exp = Experiment(id="test-123", name="Test Experiment")
        
        exp_list.add(exp)
        assert exp_list.count == 1
        
        exp_list.remove("test-123")
        assert exp_list.count == 0
        assert exp_list.get("test-123") is None
    
    def test_filter_by_status(self):
        """Test filtering experiments by status."""
        exp_list = ExperimentList()
        
        # Add a running experiment
        exp1 = Experiment(id="test-1", name="Running Experiment")
        exp_list.add(exp1)
        
        # Add a completed experiment
        exp2 = Experiment(id="test-2", name="Completed Experiment")
        exp2.complete()
        exp_list.add(exp2)
        
        # Add a failed experiment
        exp3 = Experiment(id="test-3", name="Failed Experiment")
        exp3.fail("Error")
        exp_list.add(exp3)
        
        # Filter by running status
        running = exp_list.filter(status=ExperimentStatus.RUNNING)
        assert running.count == 1
        assert running.get("test-1") is not None
        
        # Filter by completed status
        completed = exp_list.filter(status=ExperimentStatus.COMPLETED)
        assert completed.count == 1
        assert completed.get("test-2") is not None
        
        # Filter by error status
        failed = exp_list.filter(status=ExperimentStatus.ERROR)
        assert failed.count == 1
        assert failed.get("test-3") is not None
    
    def test_filter_by_tags(self):
        """Test filtering experiments by tags."""
        exp_list = ExperimentList()
        
        # Add experiments with different tags
        exp1 = Experiment(id="test-1", name="Experiment 1", tags=["tag1", "tag2"])
        exp2 = Experiment(id="test-2", name="Experiment 2", tags=["tag2", "tag3"])
        exp3 = Experiment(id="test-3", name="Experiment 3", tags=["tag1", "tag3"])
        
        exp_list.add(exp1)
        exp_list.add(exp2)
        exp_list.add(exp3)
        
        # Filter by tag1
        tag1_exps = exp_list.filter(tags=["tag1"])
        assert tag1_exps.count == 2
        assert tag1_exps.get("test-1") is not None
        assert tag1_exps.get("test-3") is not None
        
        # Filter by tag2
        tag2_exps = exp_list.filter(tags=["tag2"])
        assert tag2_exps.count == 2
        assert tag2_exps.get("test-1") is not None
        assert tag2_exps.get("test-2") is not None
        
        # Filter by tag1 and tag3
        tag13_exps = exp_list.filter(tags=["tag1", "tag3"])
        assert tag13_exps.count == 1
        assert tag13_exps.get("test-3") is not None


@pytest.fixture
def mock_app_dir():
    """Fixture to mock the application directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("expman.models.storage.get_app_dir", return_value=Path(temp_dir)):
            yield temp_dir


class TestExperimentAPI:
    """Tests for the experiment API."""
    
    def test_experiment_context_manager(self, mock_app_dir):
        """Test the experiment context manager."""
        with experiment("Test Experiment", {"param": "value"}) as exp:
            assert exp.name == "Test Experiment"
            assert exp.config == {"param": "value"}
            assert exp.status == ExperimentStatus.RUNNING
            
            # Set a metric
            exp.set_metric("accuracy", 0.95)
        
        # Check that the experiment was completed
        assert exp.status == ExperimentStatus.COMPLETED
        assert exp.end_time is not None
        
        # Check that the experiment was saved
        experiments = load_experiments()
        assert experiments.count == 1
        saved_exp = experiments.get(exp.id)
        assert saved_exp is not None
        assert saved_exp.name == "Test Experiment"
        assert saved_exp.metrics["accuracy"] == 0.95
    
    def test_experiment_context_manager_with_error(self, mock_app_dir):
        """Test the experiment context manager with an error."""
        try:
            with experiment("Test Experiment") as exp:
                assert exp.status == ExperimentStatus.RUNNING
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Check that the experiment was marked as failed
        assert exp.status == ExperimentStatus.ERROR
        assert exp.error == "Test error"
        assert exp.end_time is not None
        
        # Check that the experiment was saved
        experiments = load_experiments()
        assert experiments.count == 1
        saved_exp = experiments.get(exp.id)
        assert saved_exp is not None
        assert saved_exp.status == ExperimentStatus.ERROR
        assert saved_exp.error == "Test error"
    
    def test_save_model(self, mock_app_dir):
        """Test saving a Pydantic model."""
        with experiment("Test Experiment") as exp:
            # Create a model to save
            class TestModel(BaseModel):
                name: str
                value: int
            
            model = TestModel(name="test", value=42)
            
            # Save the model
            path = save_model(model, "test_model", exp.id)
            
            # Check that the file was created
            assert path.exists()
            
            # Check that the artifact was added to the experiment in storage
            # (Note: The current experiment object won't be updated automatically)
            updated_experiments = load_experiments()
            updated_exp = updated_experiments.get(exp.id)
            assert updated_exp is not None
            assert "test_model" in updated_exp.artifacts
            assert str(updated_exp.artifacts["test_model"]) == str(path)
    
    def test_save_dict(self, mock_app_dir):
        """Test saving a dictionary."""
        with experiment("Test Experiment") as exp:
            # Create a dictionary to save
            data = {"name": "test", "value": 42}
            
            # Save the dictionary
            path = save_dict(data, "test_dict", exp.id)
            
            # Check that the file was created
            assert path.exists()
            
            # Check that the artifact was added to the experiment in storage
            # (Note: The current experiment object won't be updated automatically)
            updated_experiments = load_experiments()
            updated_exp = updated_experiments.get(exp.id)
            assert updated_exp is not None
            assert "test_dict" in updated_exp.artifacts
            assert str(updated_exp.artifacts["test_dict"]) == str(path)