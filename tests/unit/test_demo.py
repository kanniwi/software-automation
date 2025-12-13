def test_intentional_failure():
    """Тест, который всегда падает"""
    assert 1 == 2

def test_divide_by_zero():
    result = 10 / 0  
    assert result > 0