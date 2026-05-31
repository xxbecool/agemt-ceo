"""Utility functions for ExecutiveAI backend."""
from utils.helpers import get_date_range, format_currency, format_pct, calculate_growth

# Aliases for backwards compat
paginate = None
format_percentage = format_pct
calculate_growth_pct = calculate_growth


def date_range(start, end):
    from datetime import timedelta
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


__all__ = [
    "get_date_range",
    "format_currency",
    "format_pct",
    "format_percentage",
    "calculate_growth",
    "calculate_growth_pct",
    "date_range",
]
