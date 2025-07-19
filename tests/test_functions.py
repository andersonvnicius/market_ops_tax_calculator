from decimal import Decimal
from main import (
    TAX_FREE_LARGE_OPERATIONS_THRESHOLD,
    calculate_operation_profit_tax,
    calculate_operation_total_volume,
    calculate_sell_operation_profit,
    calculate_tax_on_large_operation,
    calculate_weighted_avg,
)


# Tests for calculate_weighted_avg
def test_standard_weighted_avg():
    """Test standard case for weighted average calculation"""
    result = calculate_weighted_avg(
        current_share_qty=100,
        current_weighted_average=Decimal("10.00"),
        buy_share_qty=100,
        buy_share_value=20.00,
    )
    assert result == Decimal(
        "15.00"
    ), "Should calculate correct weighted average when buying additional shares"


def test_weighted_avg_with_zero_current():
    """Test weighted average when starting with zero shares"""
    result = calculate_weighted_avg(
        current_share_qty=0,
        current_weighted_average=Decimal("0.00"),
        buy_share_qty=100,
        buy_share_value=15.00,
    )
    assert result == Decimal(
        "15.00"
    ), "With zero current shares, should equal the buy price"


# Tests for calculate_operation_total_volume
def test_standard_volume():
    """Test standard volume calculation"""
    result = calculate_operation_total_volume(10.00, 5)
    assert result == Decimal(
        "50.00"
    ), "Should correctly calculate total volume (price * quantity)"


def test_volume_with_zero_quantity():
    """Test volume calculation with zero quantity"""
    result = calculate_operation_total_volume(10.00, 0)
    assert result == Decimal("0.00"), "Volume should be zero when quantity is zero"


def test_volume_with_zero_price():
    """Test volume calculation with zero price"""
    result = calculate_operation_total_volume(0.00, 5)
    assert result == Decimal("0.00"), "Volume should be zero when price is zero"


# Tests for calculate_sell_operation_profit
def test_profit_positive():
    """Test profit calculation when sell price > weighted average"""
    result = calculate_sell_operation_profit(
        sell_qty=10, sell_unit_cost=15.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal(
        "50.00"
    ), "Should calculate positive profit correctly (15 - 10) * 10 = 50"


def test_profit_zero():
    """Test profit calculation when sell price equals weighted average"""
    result = calculate_sell_operation_profit(
        sell_qty=5, sell_unit_cost=20.00, current_weighted_average=Decimal("20.00")
    )
    assert result == Decimal(
        "0.00"
    ), "Profit should be zero when sell price equals cost basis"


def test_profit_negative():
    """Test profit calculation when sell price < weighted average"""
    result = calculate_sell_operation_profit(
        sell_qty=3, sell_unit_cost=9.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal(
        "-3.00"
    ), "Should calculate negative profit correctly (9 - 10) * 3 = -3"


def test_profit_with_zero_quantity():
    """Test profit calculation with zero quantity sold"""
    result = calculate_sell_operation_profit(
        sell_qty=0, sell_unit_cost=15.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal("0.00"), "Profit should be zero when quantity sold is zero"


# Tests for calculate_operation_profit_tax
def test_operation_profit_tax_profit_no_accumulated_loss():
    """Test tax calculation when there's profit and no accumulated loss"""
    result = calculate_operation_profit_tax(operation_profit=Decimal("1000"))
    assert result == Decimal("200"), "Should apply tax rate to full profit"


def test_operation_profit_tax_with_accumulated_loss():
    """Test tax calculation when profit exceeds accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("500")
    )
    assert result == Decimal("100"), "Should apply tax rate to (profit - loss)"


def test_operation_loss_tax():
    """Test that no tax is applied when operation shows a loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("-1000"), current_loss=Decimal("500")
    )
    assert result == 0, "Should return 0 when profit is negative"


def test_operation_profit_tax_with_accumulated_loss_higher_than_current():
    """Test that no tax is applied when accumulated loss exceeds profit"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("1500")
    )
    assert result == 0, "Should return 0 when loss > profit"


def test_operation_profit_equals_accumulated_loss():
    """Test edge case where profit exactly equals accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("1000")
    )
    assert result == 0, "Should return 0 when profit exactly equals loss"


def test_zero_profit_with_accumulated_loss():
    """Test case with zero profit and some accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("0"), current_loss=Decimal("500")
    )
    assert result == 0, "Should return 0 when profit is zero"


# Tests for calculate_tax_on_large_operation
def test_below_threshold_no_tax():
    """Test that no tax is applied when operation volume is below threshold"""
    result = calculate_tax_on_large_operation(
        operation_unit_cost=100.00,
        operation_quantity=100,  # 100 * 100 = 10,000 < 20,000 threshold
        current_position_profit=Decimal("5000.00"),
        operation_profit=Decimal("2000.00"),
    )
    assert result == Decimal("0.00"), "Should return 0 when below volume threshold"


def test_above_threshold_with_profit():
    """Test tax calculation when operation exceeds threshold and has profit"""
    operation_profit = Decimal("5000.00")
    expected_tax = calculate_operation_profit_tax(operation_profit)

    result = calculate_tax_on_large_operation(
        operation_unit_cost=300.00,
        operation_quantity=100,  # 300 * 100 = 30,000 > 20,000 threshold
        current_position_profit=Decimal("10000.00"),
        operation_profit=operation_profit,
    )
    assert (
        result == expected_tax
    ), "Should calculate tax when above threshold with profit"


def test_above_threshold_with_loss():
    """Test no tax when operation exceeds threshold but has overall loss"""
    result = calculate_tax_on_large_operation(
        operation_unit_cost=300.00,
        operation_quantity=100,  # 30,000 > threshold
        current_position_profit=Decimal("-5000.00"),  # negative profit
        operation_profit=Decimal("2000.00"),
    )
    # Should apply loss offset (2000 - 5000 = -3000) which results in 0 tax
    assert result == Decimal(
        "0.00"
    ), "Should return 0 when effective profit is negative"


def test_negative_profit_operation():
    """Test with negative operation profit (should result in 0 tax)"""
    result = calculate_tax_on_large_operation(
        operation_unit_cost=300.00,
        operation_quantity=100,  # 30,000 > threshold
        current_position_profit=Decimal("5000.00"),
        operation_profit=Decimal("-2000.00"),  # negative profit
    )
    assert result == Decimal(
        "0.00"
    ), "Should return 0 when operation profit is negative"


# TESTING DECIMAL PRECISION !!
def test_precision_calculation():
    """Test that decimal precision is maintained in calculations"""
    result = calculate_tax_on_large_operation(
        operation_unit_cost=200.01,
        operation_quantity=100,  # 20,001 > 20,000 threshold
        current_position_profit=Decimal("1234.56"),
        operation_profit=Decimal("789.01"),
    )
    # Verify the calculation maintains precision
    expected_volume = Decimal("200.01") * 100
    assert expected_volume > TAX_FREE_LARGE_OPERATIONS_THRESHOLD
    assert isinstance(result, Decimal), "Result should maintain Decimal type"
