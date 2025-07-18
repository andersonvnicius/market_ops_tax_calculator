from decimal import Decimal
import json

from utils.decorators import round_decimal_output
from utils.json_utils import decimal_default

TAX_RATE_ON_PROFIT = Decimal(0.2)
TAX_FREE_OPERATION_LIMIT = Decimal(20000)

@round_decimal_output()
def calculate_weighted_avg(
    current_share_qty: int,
    current_avg_weighted: Decimal,
    buy_share_qty: int,
    buy_share_value: float,
) -> Decimal:
    weighted_avg = (
        (current_share_qty * current_avg_weighted)
        + (buy_share_qty * Decimal(buy_share_value))
    ) / (current_share_qty + buy_share_qty)
    return weighted_avg


@round_decimal_output()
def calculate_operation_total_volume(unit_cost: float, quantity: int) -> Decimal:
    return Decimal(unit_cost) * Decimal(quantity)


@round_decimal_output()
def calculate_sell_operation_profit(
    sell_qty: int, sell_unit_cost: float, current_avg_weighted: Decimal
) -> Decimal:
    return sell_qty * (Decimal(sell_unit_cost) - current_avg_weighted)


@round_decimal_output()
def calculate_operation_profit_tax(
    operation_profit: Decimal, current_loss: Decimal = Decimal(0)
) -> Decimal:
    if operation_profit < 0:
        return 0
    return TAX_RATE_ON_PROFIT * (operation_profit + current_loss)


def get_market_operations_tax_list(operation_list: list[dict]) -> list[dict]:
    """
    Input:
        operation_list: list[dict]
    Output:
        operations_tax_list: list[dict[str, Decimal]]
    """
    # The first operation must always be a buy, so the first values for
    # avg share price, share qty and profit are directly the values that
    # arrive in the first operation in the input data
    current_position = {
        "cur_avg_weighted": Decimal(operation_list[0]["unit-cost"]),
        "cur_qty_shares": operation_list[0]["quantity"],
        "cur_profit": Decimal(0),
    }
    # First value for tax will always be zero
    operations_tax_list = [{"tax": Decimal(0)}]

    # Iterating through operations
    for operation in operation_list[1:]:
        tax_value = 0

        # Only sell operations needs to have profits and taxes being calculated
        # and applied
        if operation["operation"] == "sell":
            # Calculating operation profit, can be negative (loss)
            operation_profit = calculate_sell_operation_profit(
                operation["quantity"],
                operation["unit-cost"],
                current_position["cur_avg_weighted"],
            )
            # If the total volume of the operation is less then the volume
            # threshold, no taxes are applied
            if (
                calculate_operation_total_volume(
                    operation["unit-cost"], operation["quantity"]
                )
                > TAX_FREE_OPERATION_LIMIT
            ):
                # Getting loss from the current position (or zero)
                current_loss = (
                    current_position["cur_profit"]
                    if current_position["cur_profit"] < 0
                    else 0
                )
                # Calculating tax value for the operation
                tax_value = calculate_operation_profit_tax(
                        operation_profit, current_loss
                    )

            # Updating current position data
            current_position["cur_profit"] += operation_profit
            current_position["cur_qty_shares"] -= operation["quantity"]
        else:
            # calculates new values for share qty and weighted avg, saves in memory
            current_position["cur_avg_weighted"] = calculate_weighted_avg(
                current_share_qty=current_position["cur_qty_shares"],
                current_avg_weighted=current_position["cur_avg_weighted"],
                buy_share_qty=operation["quantity"],
                buy_share_value=operation["unit-cost"],
            )
            current_position["cur_qty_shares"] += operation["quantity"]

        operations_tax_list.append({"tax": tax_value})

    return json.dumps(operations_tax_list, default=decimal_default)


if __name__ == "__main__":
    operation_list = [
        {"operation": "buy", "unit-cost": 10.00, "quantity": 100000},
        {"operation": "sell", "unit-cost": 20.00, "quantity": 5000},
        {"operation": "sell", "unit-cost": 15.00, "quantity": 5000},
    ]
    print(get_market_operations_tax_list(operation_list))
