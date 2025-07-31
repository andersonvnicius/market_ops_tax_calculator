from decimal import Decimal
import json
from main import orchestrator


def test_single_buy_operation():
    """Test with just a single buy operation (should return [0])"""
    operations = [{"operation": "buy", "unit-cost": 10.00, "quantity": 100}]
    result = json.loads(orchestrator(operations))
    assert result == [{"tax": "0.00"}]


def test_buy_then_sell_below_threshold():
    """Test buy followed by sell below large operation threshold"""
    operations = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 100},
        {
            "operation": "sell",
            "unit-cost": 15.00,
            "quantity": 10,
        },  # 150 < 20k threshold
    ]
    result = json.loads(orchestrator(operations))
    assert result == [{"tax": "0.00"}, {"tax": "0.00"}]


def test_buy_then_sell_above_threshold_with_profit():
    """Test buy followed by large sell with profit"""
    operations = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 10000},
        {
            "operation": "sell",
            "unit-cost": 20.00,
            "quantity": 2000,
        },  # 20,000 = threshold
    ]
    result = json.loads(orchestrator(operations))
    assert result[1]["tax"] == "4000.00"


def test_multiple_operations_with_loss():
    """Test sequence with losing trades"""
    operations = [
        {"operation": "buy", "unit-cost": 50.00, "quantity": 100},
        {
            "operation": "sell",
            "unit-cost": 40.00,
            "quantity": 50,
        },  # 2,000 < threshold, loss
        {"operation": "sell", "unit-cost": 60.00, "quantity": 50},  # 3,000 < threshold
    ]
    result = json.loads(orchestrator(operations))
    assert result[1]["tax"] == "0.00"  # First sell at loss
    assert result[2]["tax"] == "0.00"  # Second sell recovers loss (no net profit)


def test_large_sell_with_previous_loss():
    """Test large sell operation after previous loss"""
    operations = [
        {"operation": "buy", "unit-cost": 30.00, "quantity": 1000},
        {
            "operation": "sell",
            "unit-cost": 20.00,
            "quantity": 500,
        },  # 10,000 < threshold, loss
        {
            "operation": "sell",
            "unit-cost": 40.00,
            "quantity": 500,
        },  # 20,000 = threshold
    ]
    result = json.loads(orchestrator(operations))
    # First sell: 500*(20-30) = -5000 loss
    # Second sell: 500*(40-30) = 5000 profit
    # Net profit: 0, so tax should be 0
    assert result[2]["tax"] == "0.00"


def test_position_reset_after_full_sell():
    """Test profit reset when all shares are sold"""
    operations = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 10000},
        {"operation": "sell", "unit-cost": 20.00, "quantity": 10000},  # Full sell
        {"operation": "buy", "unit-cost": 15.00, "quantity": 5000},
        {"operation": "sell", "unit-cost": 25.00, "quantity": 5000},  # New position
    ]
    result = json.loads(orchestrator(operations))
    # First sell: 10000*(20-10) = 100000 profit
    # Second sell: 5000*(25-15) = 50000 profit
    assert result[1]["tax"] == "20000.00"
    assert result[3]["tax"] == "10000.00"


def test_multiple_buys_before_sell():
    """Test weighted average calculation with multiple buys"""
    operations = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 10000},
        {"operation": "buy", "unit-cost": 20.00, "quantity": 10000},
        {
            "operation": "sell",
            "unit-cost": 25.00,
            "quantity": 15000,
        },  # 3,750 < threshold
    ]
    result = json.loads(orchestrator(operations))
    # Weighted avg: (10*10000 + 20*10000)/20000 = 15
    # Profit: (25-15)*15000 = 1500000
    assert result[2]["tax"] == "30000.00"  # Below threshold


def test_large_operation_with_fractional_profit():
    """Test precision with fractional values""" 
    operations = [
        {"operation": "buy", "unit-cost": 10.555, "quantity": 1000},
        {
            "operation": "sell",
            "unit-cost": 20.123,
            "quantity": 1000,
        },  # 20,123 > threshold
    ]
    result = json.loads(orchestrator(operations))
    profit = (Decimal("20.123") - Decimal("10.555")) * 1000
    expected_tax = (profit * Decimal("0.2")).quantize(Decimal("0.00"))
    assert Decimal(str(result[1]["tax"])).quantize(Decimal("0.00")) == expected_tax


def test_buy_then_sell_more_than_available():
    """Test buy followed by sell over available qty"""
    operations = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 100},
        {
            "operation": "sell",
            "unit-cost": 12.00,
            "quantity": 1000,
        },  # 150 < 20k threshold
    ]
    result = json.loads(orchestrator(operations))
    assert result == [{"tax": "0.00"}, {"error": "Can't sell more stocks than you have"}]
