"""Tests for the test pipeline."""

import sys
from pathlib import Path

# Add repo root to path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_pipeline_import():
    """Test that the pipeline module can be imported."""
    from pipelines.training.test_pipeline import example_pipelines
    
    assert hasattr(example_pipelines, 'test_pipeline')
    assert hasattr(example_pipelines, 'simple_pipeline')
    assert callable(example_pipelines.test_pipeline)
    assert callable(example_pipelines.simple_pipeline)


def test_pipeline_functions_exist():
    """Test that pipeline functions are defined."""
    from pipelines.training.test_pipeline import example_pipelines
    
    # Check that functions exist
    assert example_pipelines.test_pipeline is not None
    assert example_pipelines.simple_pipeline is not None

