"""Утилиты форматирования строк для UI."""

def format_time_seconds(seconds: float) -> str:
    """Возвращает время в формате MM:SS с усечением вниз."""
    total = max(0, int(seconds))
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}:{secs:02d}"
