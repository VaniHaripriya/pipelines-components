# Test Component

A simple test component demonstrating the structure and testing patterns for Kubeflow Pipelines components.

## Overview

This component processes input data by applying a multiplier. It serves as an example for:

- Component structure and organization
- Writing unit tests
- Running tests with the test runner script

## Inputs

- `input_data` (str): The input data string to process
- `multiplier` (int, default=2): The multiplier to apply to the input

## Outputs

- Returns (str): The processed data (input repeated multiplier times)

## Usage Example

```python
from kfp import dsl
from kfp_components.components.data_processing.test_component import process_data

@dsl.pipeline(name="test-component-pipeline")
def example_pipeline(input_str: str = "test"):
    result = process_data(input_data=input_str, multiplier=3)
    return result
```

## Running Tests

To run tests for this component:

```bash
# From the repository root
python scripts/tests/run_component_tests.py components/data_processing/test_component
```

Or run pytest directly:

```bash
cd components/data_processing/test_component
pytest tests/ -v
```

## Development

This is a demonstration component. For production components, ensure:

- Comprehensive test coverage
- Proper error handling
- Documentation
- Metadata.yaml is complete and accurate
