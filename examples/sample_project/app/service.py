def calculate_total(items: list[float]) -> float:
    """Return the sum of item prices."""
    return sum(items)

def format_total(total: float) -> str:
    """Format a total for display."""
    return f"${total:.2f}"
