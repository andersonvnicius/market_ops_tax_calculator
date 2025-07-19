from decimal import Decimal
from main import (
    TAX_FREE_LARGE_OPERATIONS_THRESHOLD,
    calculate_operation_profit_tax,
    calculate_operation_total_volume,
    calculate_sell_operation_profit_or_loss,
    calculate_current_position_loss,
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
    )  # Should calculate correct weighted average when buying additional shares"


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
    )  # With zero current shares, should equal the buy price"


# Tests for calculate_operation_total_volume
def test_standard_volume():
    """Test standard volume calculation"""
    result = calculate_operation_total_volume(10.00, 5)
    assert result == Decimal(
        "50.00"
    )  # Should correctly calculate total volume (price * quantity)"


def test_volume_with_zero_quantity():
    """Test volume calculation with zero quantity"""
    result = calculate_operation_total_volume(10.00, 0)
    assert result == Decimal("0.00")  # Volume should be zero when quantity is zero"


def test_volume_with_zero_price():
    """Test volume calculation with zero price"""
    result = calculate_operation_total_volume(0.00, 5)
    assert result == Decimal("0.00")  # Volume should be zero when price is zero"


# Tests for calculate_sell_operation_profit
def test_profit_positive():
    """Test profit calculation when sell price > weighted average"""
    result = calculate_sell_operation_profit_or_loss(
        sell_qty=10, sell_unit_cost=15.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal(
        "50.00"
    )  # Should calculate positive profit correctly (15 - 10) * 10 = 50"


def test_profit_zero():
    """Test profit calculation when sell price equals weighted average"""
    result = calculate_sell_operation_profit_or_loss(
        sell_qty=5, sell_unit_cost=20.00, current_weighted_average=Decimal("20.00")
    )
    assert result == Decimal(
        "0.00"
    )  # Profit should be zero when sell price equals cost basis"


def test_profit_negative():
    """Test profit calculation when sell price < weighted average"""
    result = calculate_sell_operation_profit_or_loss(
        sell_qty=3, sell_unit_cost=9.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal(
        "-3.00"
    )  # Should calculate negative profit correctly (9 - 10) * 3 = -3"


def test_profit_with_zero_quantity():
    """Test profit calculation with zero quantity sold"""
    result = calculate_sell_operation_profit_or_loss(
        sell_qty=0, sell_unit_cost=15.00, current_weighted_average=Decimal("10.00")
    )
    assert result == Decimal(
        "0.00"
    )  # Profit should be zero when quantity sold is zero"


# Tests for calculate_operation_profit_tax
def test_operation_profit_tax_profit_no_accumulated_loss():
    """Test tax calculation when there's profit and no accumulated loss"""
    result = calculate_operation_profit_tax(operation_profit=Decimal("1000"))
    assert result == Decimal("200")  # Should apply tax rate to full profit"


def test_operation_profit_tax_with_accumulated_loss():
    """Test tax calculation when profit exceeds accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("500")
    )
    assert result == Decimal("100")  # Should apply tax rate to (profit - loss)"


def test_operation_loss_tax():
    """Test that no tax is applied when operation shows a loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("-1000"), current_loss=Decimal("500")
    )
    assert result == 0  # Should return 0 when profit is negative"


def test_operation_profit_tax_with_accumulated_loss_higher_than_current():
    """Test that no tax is applied when accumulated loss exceeds profit"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("1500")
    )
    assert result == 0  # Should return 0 when loss > profit"


def test_operation_profit_equals_accumulated_loss():
    """Test edge case where profit exactly equals accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("1000"), current_loss=Decimal("1000")
    )
    assert result == 0  # Should return 0 when profit exactly equals loss"


def test_zero_profit_with_accumulated_loss():
    """Test case with zero profit and some accumulated loss"""
    result = calculate_operation_profit_tax(
        operation_profit=Decimal("0"), current_loss=Decimal("500")
    )
    assert result == 0  # Should return 0 when profit is zero"


# Tests for calculate_current_position_loss
def test_calculate_current_position_loss_loss_operation_adds_to_loss():
    """Test case where a loss operation increases the current accumulated loss"""
    current_loss = Decimal("100")
    operation_profit_or_loss = Decimal("-50")
    result = calculate_current_position_loss(
        current_loss,
        operation_profit_or_loss,
        _is_operation_over_volume_threshold=False,
    )
    assert result == Decimal("150")  # Loss should be added to current loss


def test_calculate_current_position_loss_profit_operation_above_threshold_reduces_loss():
    """Test case where a profit above volume threshold reduces the accumulated loss"""
    current_loss = Decimal("100")
    operation_profit_or_loss = Decimal("30")
    result = calculate_current_position_loss(
        current_loss, operation_profit_or_loss, _is_operation_over_volume_threshold=True
    )
    assert result == Decimal("70")  # Profit reduces the loss by its value


def test_calculate_current_position_loss_profit_operation_above_threshold_resets_loss_to_zero():
    """Test case where profit above threshold is larger than loss and resets it to zero"""
    current_loss = Decimal("20")
    operation_profit_or_loss = Decimal("50")
    result = calculate_current_position_loss(
        current_loss, operation_profit_or_loss, _is_operation_over_volume_threshold=True
    )
    assert result == Decimal("0")  # Profit > loss, so loss is reset to 0


def test_calculate_current_position_loss_profit_operation_below_threshold_does_not_affect_loss():
    """Test case where profit below threshold does not reduce accumulated loss"""
    current_loss = Decimal("80")
    operation_profit_or_loss = Decimal("30")
    result = calculate_current_position_loss(
        current_loss,
        operation_profit_or_loss,
        _is_operation_over_volume_threshold=False,
    )
    assert result == Decimal("80")  # Profit ignored since it's below the threshold
