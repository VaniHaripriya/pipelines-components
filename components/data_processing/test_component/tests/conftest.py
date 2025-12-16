"""Pytest configuration for test component tests."""

import sys
from pathlib import Path

# Add the component directory to the path for imports
_COMPONENT_DIR = Path(__file__).resolve().parent.parent
if str(_COMPONENT_DIR) not in sys.path:
    sys.path.insert(0, str(_COMPONENT_DIR))
