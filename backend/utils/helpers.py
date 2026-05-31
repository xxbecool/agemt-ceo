from datetime import date, timedelta
from typing import List, Tuple


def get_date_range(period: str) -> Tuple[date, date]:
    end = date.today()
    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "365d": 365}
    days = days_map.get(period, 30)
    return end - timedelta(days=days), end


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_pct(value: float) -> str:
    return f"{value:+.1f}%"


def calculate_growth(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 2)


def chunk_list(lst: List, size: int) -> List[List]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]
