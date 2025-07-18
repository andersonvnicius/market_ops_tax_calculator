from decimal import Decimal
from main import get_market_operations_tax_list


def test_main():
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
