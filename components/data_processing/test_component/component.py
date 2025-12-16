"""Test component for Kubeflow Pipelines."""

from kfp import dsl


@dsl.component
def process_data(input_data: str, multiplier: int = 2) -> str:
    """Process input data by applying a multiplier.

    This is a simple test component that demonstrates the structure
    and testing patterns for Kubeflow Pipelines components.

    Args:
        input_data: The input data string to process.
        multiplier: The multiplier to apply (default: 2).

    Returns:
        The processed data as a string.
    """
    result = input_data * multiplier
    print(f"Processing: {input_data} with multiplier {multiplier}")
    print(f"Result: {result}")
    return result
