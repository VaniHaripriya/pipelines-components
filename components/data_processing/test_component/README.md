# Test-component ✨

## Overview 🧾

Process input data by applying a multiplier.

This is a simple test component that demonstrates the structure
and testing patterns for Kubeflow Pipelines components.

## Inputs 📥

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_data` | `str` | `None` | The input data string to process. |
| `multiplier` | `int` | `2` | The multiplier to apply (default: 2). |

## Outputs 📤

| Name | Type | Description |
|------|------|-------------|
| Output | `str` | The processed data as a string. |

## Usage Examples 🧪

```python
"""Example pipelines demonstrating usage of the test component."""

import sys
from pathlib import Path

from kfp import dsl

_component_dir = Path(__file__).resolve().parent
if str(_component_dir) not in sys.path:
    sys.path.insert(0, str(_component_dir))

from component import process_data


@dsl.pipeline(name="test-component-simple-pipeline")
def simple_pipeline(input_str: str = "hello") -> str:
    """Simple pipeline demonstrating basic usage of process_data component.

    Args:
        input_str: Input string to process (default: "hello").

    Returns:
        Processed output string.
    """
    result = process_data(input_data=input_str, multiplier=2)
    return result.output


@dsl.pipeline(name="test-component-advanced-pipeline")
def advanced_pipeline(input_str: str = "test", multiplier: int = 3) -> str:
    """Advanced pipeline demonstrating process_data with custom multiplier.

    Args:
        input_str: Input string to process (default: "test").
        multiplier: Custom multiplier value (default: 3).

    Returns:
        Processed output string.
    """
    result = process_data(input_data=input_str, multiplier=multiplier)
    return result.output

```

## Metadata 🗂️

- **Name**: test-component
- **Stability**: alpha
- **Dependencies**:
  - Kubeflow:
    - Name: Pipelines, Version: >=2.15.0
- **Tags**:
  - data-processing
  - example
  - test
- **Last Verified**: 2025-01-15T00:00:00Z
- **Owners**:
  - Approvers:
    - kubeflow-maintainers
  - Reviewers:
    - kubeflow-maintainers

## Additional Resources 📚

- **Documentation**: [https://kubeflow.org/components/test-component](https://kubeflow.org/components/test-component)
- **Issue Tracker**: [https://github.com/kubeflow/pipelines-components/issues](https://github.com/kubeflow/pipelines-components/issues)
