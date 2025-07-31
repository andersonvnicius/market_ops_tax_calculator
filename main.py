import json
import sys
from decimal import Decimal

from calculations import (
    calculate_current_position_loss,
    calculate_operation_profit_tax,
    calculate_operation_total_volume,
    calculate_sell_operation_profit_or_loss,
    calculate_weighted_avg,
)
from tax_operations_constants import TAX_FREE_LARGE_OPERATIONS_THRESHOLD, TAX_OVERSELL_ERROR_MESSAGE
from utils.json_utils import decimal_default


def orchestrator(operation_list: list[dict]) -> list[dict]:
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
    output_values = [{"tax": Decimal(0)}]

    for operation in operation_list[1:]:
        tax = 0

        if operation["operation"] == "sell":
            if operation["quantity"] > current_position["share_quantity"]:
                output_values.append({"error": TAX_OVERSELL_ERROR_MESSAGE})
                continue

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

        output_values.append({"tax": Decimal(tax)})

    return json.dumps(output_values, default=decimal_default)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            operation_list = json.loads(line)
            tax_result = orchestrator(operation_list)
            print(tax_result)
        except Exception as e:
            print(f"Error processing line: {e}", file=sys.stderr)


if __name__ == "__main__":
    # out = orchestrator(
    #     operation_list=[
    #         {"operation": "buy",  "unit-cost": 10, "quantity": 10000}, 
    #         {"operation": "sell", "unit-cost": 21122.10, "quantity": 1000},
    #         {"operation": "sell", "unit-cost": 21122.10, "quantity": 1000}
    #     ]
    # )
    # print(out)
    main()
