from app.service import calculate_total, format_total

def checkout(items: list[float]) -> dict[str, str]:
    total = calculate_total(items)
    return {"total": format_total(total)}
