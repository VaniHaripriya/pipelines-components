"""Tests for the test component."""

import sys
from pathlib import Path

# Add repo root to path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def test_component_import():
    """Test that the component can be imported."""
    from components.training.test_component import component
    
    assert hasattr(component, 'test_component')
    assert callable(component.test_component)


def test_component_functionality():
    """Test the component functionality."""
    from components.training.test_component import component
    
    result = component.test_component("test")
    assert result == "Processed: test"
    
    # Test with default
    result_default = component.test_component()
    assert result_default == "Processed: Hello"

