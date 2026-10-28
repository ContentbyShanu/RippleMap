from app.service import calculate_total

def summarize_batch(batch: list[list[float]]) -> list[float]:
    return [calculate_total(items) for items in batch]
