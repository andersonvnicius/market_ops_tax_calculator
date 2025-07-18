from decimal import Decimal
from main import calculate_operation_total_volume, calculate_sell_operation_profit, calculate_weighted_avg


def test_standard_weighted_avg():
    result = calculate_weighted_avg(
        current_share_qty=100,
        current_avg_weighted=Decimal("10.00"),
        buy_share_qty=100,
        buy_share_value=20.00,
    )
    assert result == Decimal("15.00")


def test_standard_volume():
    result = calculate_operation_total_volume(10.00, 5)
    assert result == Decimal("50.00")


def test_profit_positive():
    result = calculate_sell_operation_profit(
        sell_qty=10,
        sell_unit_cost=15.00,
        current_avg_weighted=Decimal("10.00")
    )
    assert result == Decimal("50.00")  # (15 - 10) * 10 = 50


def test_profit_zero():
    result = calculate_sell_operation_profit(
        sell_qty=5,
        sell_unit_cost=20.00,
        current_avg_weighted=Decimal("20.00")
    )
    assert result == Decimal("0.00")


def test_profit_negative():
    result = calculate_sell_operation_profit(
        sell_qty=3,
        sell_unit_cost=9.00,
        current_avg_weighted=Decimal("10.00")
    )
    assert result == Decimal("-3.00")  # (9 - 10) * 3



