from decimal import Decimal
import json

from utils.decorators import round_decimal_output
from utils.json_utils import decimal_default

TAX_RATE_ON_PROFIT = Decimal("0.2")
TAX_FREE_LARGE_OPERATIONS_THRESHOLD = Decimal("20000")


@round_decimal_output()
def calculate_operation_total_volume(unit_cost: float, quantity: int) -> Decimal:
    """Calculate the total monetary volume of an operation."""
    return Decimal(unit_cost) * Decimal(quantity)


@round_decimal_output()
def calculate_sell_operation_profit(
    sell_qty: int, sell_unit_cost: float, current_weighted_average: Decimal
) -> Decimal:
    """Calculate the profit (or loss) from a sell operation."""
    return sell_qty * (Decimal(sell_unit_cost) - current_weighted_average)


@round_decimal_output()
def calculate_operation_profit_tax(
    operation_profit: Decimal, current_loss: Decimal = Decimal(0)
) -> Decimal:
    """Calculate the tax owed on a profitable sell operation."""
    if operation_profit < 0 or operation_profit < current_loss:
        return 0
    return TAX_RATE_ON_PROFIT * (operation_profit - current_loss)


def calculate_tax_on_large_operation(
    operation_unit_cost: float,
    operation_quantity: int,
    current_position_profit: Decimal,
    operation_profit: Decimal,
) -> Decimal:
    """
    Determine the tax to apply on a sell operation if the transaction volume exceeds the exemption threshold.

    Args:
        operation_unit_cost (float): Price per unit in the current operation.
        operation_quantity (int): Number of units in the current operation.
        current_position_profit (Decimal): Total profit accumulated so far.
        operation_profit (Decimal): Profit from the current sell operation.

    Returns:
        Decimal: Tax amount due. Zero if below threshold.
    """
    # If the total volume of the operation is less then the volume
    # threshold, no taxes are applied
    if (
        calculate_operation_total_volume(operation_unit_cost, operation_quantity)
        > TAX_FREE_LARGE_OPERATIONS_THRESHOLD
    ):
        # Calculating tax value for the operation
        return calculate_operation_profit_tax(
            operation_profit, 
            current_loss=(
                current_position_profit * -1  # negative profit is positive loss
                if current_position_profit < 0
                else 0
            )
        )
    return 0


@round_decimal_output()
def calculate_weighted_avg(
    current_share_qty: int,
    current_weighted_average: Decimal,
    buy_share_qty: int,
    buy_share_value: float,
) -> Decimal:
    """
    Calculate the new weighted average after a buy operation.

    Args:
        current_share_qty (int): Quantity of shares currently held.
        current_avg_weighted (Decimal): Current average weighted price per share.
        buy_share_qty (int): Quantity of shares bought.
        buy_share_value (float): Price per share in the new buy operation.

    Returns:
        Decimal: New weighted average price per share.
    """
    weighted_avg = (
        (current_share_qty * current_weighted_average)
        + (buy_share_qty * Decimal(buy_share_value))
    ) / (current_share_qty + buy_share_qty)
    return weighted_avg


def get_market_operations_tax_list(operation_list: list[dict]) -> list[dict]:
    """
    Calculate taxes owed for a sequence of market operations.

    Args:
        operation_list (list[dict]): List of operations. Each operation must have:
            - "operation": either "buy" or "sell"
            - "unit-cost": float, cost per share
            - "quantity": int, number of shares

    Returns:
        str (JSON): List of dicts with tax values for each operation, serialized to JSON.
    """
    # The first operation is always a 'buy', so the initial average price, 
    # share quantity, and profit are directly taken from this first entry.
    current_position = {
        "weighted_average": Decimal(operation_list[0]["unit-cost"]),
        "share_quantity": operation_list[0]["quantity"],
        "profit": Decimal(0),
    }
    # First value for tax will always be zero
    operations_tax_list = [{"tax": Decimal(0)}]

    for operation in operation_list[1:]:
        operation_taxes = {}

        if operation["operation"] == "sell":
            operation_profit = calculate_sell_operation_profit(
                operation["quantity"],
                operation["unit-cost"],
                current_position["weighted_average"],
            )

            operation_taxes["over_big_transaction"] = calculate_tax_on_large_operation(
                operation["unit-cost"],
                operation["quantity"],
                current_position_profit=current_position["profit"],
                operation_profit=operation_profit,
            )

            current_position["profit"] += operation_profit
            current_position["share_quantity"] -= operation["quantity"]
        else:
            # calculates new values for share qty and weighted avg, saves in memory
            current_position["weighted_average"] = calculate_weighted_avg(
                current_share_qty=current_position["share_quantity"],
                current_weighted_average=current_position["weighted_average"],
                buy_share_qty=operation["quantity"],
                buy_share_value=operation["unit-cost"],
            )
            current_position["share_quantity"] += operation["quantity"]

        operations_tax_list.append({"tax": sum(operation_taxes.values())})

    return json.dumps(operations_tax_list, default=decimal_default)


if __name__ == "__main__":
    operation_list = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 100000},
        {"operation": "sell", "unit-cost": 20.00, "quantity": 5000},
        {"operation": "sell", "unit-cost": 15.00, "quantity": 5000},
    ]
    print(get_market_operations_tax_list(operation_list))
