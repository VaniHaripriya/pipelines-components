"""Tests for the test component."""

from component import process_data


def test_process_data_default_multiplier():
    """Test process_data with default multiplier."""
    result = process_data.python_func(input_data="test")
    assert result == "testtest"
    assert isinstance(result, str)


def test_process_data_custom_multiplier():
    """Test process_data with custom multiplier."""
    result = process_data.python_func(input_data="abc", multiplier=3)
    assert result == "abcabcabc"


def test_process_data_multiplier_one():
    """Test process_data with multiplier of 1."""
    result = process_data.python_func(input_data="hello", multiplier=1)
    assert result == "hello"


def test_process_data_empty_string():
    """Test process_data with empty string."""
    result = process_data.python_func(input_data="", multiplier=5)
    assert result == ""


def test_process_data_signature():
    """Test that the component has the correct signature."""
    # Verify the component can be accessed
    assert callable(process_data.python_func)

    # Test that it accepts the expected parameters
    result = process_data.python_func(input_data="test", multiplier=2)
    assert result is not None
