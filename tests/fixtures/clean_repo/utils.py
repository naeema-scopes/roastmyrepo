"""Clean utility functions."""


def is_even(number: int) -> bool:
    """Check if a number is even."""
    return number % 2 == 0


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))
