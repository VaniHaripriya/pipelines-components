"""Example pipelines demonstrating usage of the test component."""

from kfp import dsl

from .component import process_data


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
