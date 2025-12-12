"""A simple test component for CI validation."""

def test_component(input_text: str = "Hello") -> str:
    """A simple test component.
    
    Args:
        input_text: Input text to process. Defaults to "Hello".
    
    Returns:
        Processed text.
    """
    return f"Processed: {input_text}"

