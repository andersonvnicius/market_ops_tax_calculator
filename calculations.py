from decimal import Decimal

from tax_operations_constants import TAX_RATE_ON_PROFIT
from utils.decorators import round_decimal_output


def calculate_operation_total_volume(unit_cost: float, quantity: int) -> Decimal:
    """Calculate the total monetary volume of an operation."""
    return unit_cost * quantity


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
