from app.service import calculate_total, format_total

def test_calculate_total():
    assert calculate_total([2.0, 3.5]) == 5.5

def test_format_total():
    assert format_total(5) == "$5.00"
