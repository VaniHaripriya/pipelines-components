"""Example pipelines for testing the CI workflow."""

from kfp import dsl


@dsl.pipeline(
    name='test-pipeline',
    description='A simple test pipeline for CI validation'
)
def test_pipeline(
    input_text: str = "Hello, World!"
):
    """A simple test pipeline.
    
    Args:
        input_text: Text to process. Defaults to "Hello, World!".
    """
    pass  # Minimal pipeline for testing compilation


@dsl.pipeline
def simple_pipeline():
    """A minimal pipeline without parameters."""
    pass  # Minimal pipeline for testing compilation

