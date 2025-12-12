"""Example pipelines for testing the CI workflow."""

from kfp import dsl


@dsl.component
def echo_task(message: str) -> str:
    """Simple echo task for testing."""
    return message


@dsl.pipeline(
    name='test-pipeline',
    description='A simple test pipeline for CI validation'
)
def test_pipeline(
    input_text: str = "Hello, World!"
) -> str:
    """A simple test pipeline.
    
    Args:
        input_text: Text to process. Defaults to "Hello, World!".
    
    Returns:
        The processed text.
    """
    result = echo_task(message=input_text)
    return result.output


@dsl.pipeline
def simple_pipeline():
    """A minimal pipeline without parameters."""
    echo_task(message="Test")

