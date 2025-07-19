import json
import sys
from decimal import Decimal

from utils.decorators import round_decimal_output
from utils.json_utils import decimal_default

TAX_RATE_ON_PROFIT = Decimal("0.2")
TAX_FREE_LARGE_OPERATIONS_THRESHOLD = Decimal("20000")


@round_decimal_output()
def calculate_operation_total_volume(unit_cost: float, quantity: int) -> Decimal:
    """Calculate the total monetary volume of an operation."""
    return Decimal(unit_cost) * Decimal(quantity)


@round_decimal_output()
def calculate_sell_operation_profit_or_loss(
    sell_qty: int, sell_unit_cost: float, current_weighted_average: Decimal
) -> Decimal:
    """Calculate the profit or loss (if negative) from a sell operation."""
    return sell_qty * (Decimal(sell_unit_cost) - current_weighted_average)


@round_decimal_output()
def calculate_operation_profit_tax(
    operation_profit: Decimal, current_loss: Decimal = Decimal(0)
) -> Decimal:
    """Calculate the tax owed on a profitable sell operation."""
    if operation_profit < 0 or operation_profit < current_loss:
        return Decimal(0)
    return TAX_RATE_ON_PROFIT * (operation_profit - current_loss)


@round_decimal_output()
def calculate_current_position_loss(
    current_loss: Decimal,
    operation_profit_or_loss: Decimal,
    _is_operation_over_volume_threshold: bool,
) -> Decimal:
    """Updates the current accumulated loss based on the result of a new operation."""
    _is_loss_operation = True if operation_profit_or_loss < 0 else False

    if _is_loss_operation:
        current_loss -= operation_profit_or_loss
    elif _is_operation_over_volume_threshold:
        current_loss -= operation_profit_or_loss
        if current_loss < 0:
            current_loss = 0

    return current_loss


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
        "loss": Decimal(0),
    }
    # First value for tax will always be zero
    operations_tax_list = [{"tax": Decimal(0)}]

    for operation in operation_list[1:]:
        tax = 0

        if operation["operation"] == "sell":
            operation_profit_or_loss = calculate_sell_operation_profit_or_loss(
                operation["quantity"],
                operation["unit-cost"],
                current_position["weighted_average"],
            )

            _is_operation_over_volume_threshold = (
                calculate_operation_total_volume(
                    operation["unit-cost"], operation["quantity"]
                )
                > TAX_FREE_LARGE_OPERATIONS_THRESHOLD
            )

            if _is_operation_over_volume_threshold:
                # Calculating tax value for the operation
                tax = calculate_operation_profit_tax(
                    operation_profit_or_loss, current_loss=current_position["loss"]
                )

            current_position["loss"] = calculate_current_position_loss(
                current_position["loss"],
                operation_profit_or_loss,
                _is_operation_over_volume_threshold,
            )

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

        operations_tax_list.append({"tax": Decimal(tax)})

    return json.dumps(operations_tax_list, default=decimal_default)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            operation_list = json.loads(line)
            tax_result = get_market_operations_tax_list(operation_list)
            print(tax_result)
        except Exception as e:
            print(f"Error processing line: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
