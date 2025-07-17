from decimal import Decimal
from main import get_market_operations_tax_list, calculate_weighted_avg


def test_calculate_avg_weighted():
    expected_output = Decimal(15)
    output = calculate_weighted_avg(
        current_share_qty = 5,
        current_avg_weighted = Decimal(20),
        buy_share_qty = 5,
        buy_share_value = Decimal(10),
    )
    assert output == expected_output

def test_calculate_tax():
    pass

def test_orchestrator():
    operation_list = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 10000},
        {"operation": "sell", "unit-cost": 20.00, "quantity": 5000},
    ]

    expected_output = [
        {"tax": 0.00}, 
        {"tax": Decimal(10.00E3)}
    ]
    
    output = get_market_operations_tax_list(operation_list)
    assert output == expected_output
