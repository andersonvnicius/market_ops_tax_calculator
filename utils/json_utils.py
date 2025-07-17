from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def decimal_default(obj):
    if isinstance(obj, Decimal):
        try:
            # Round safely to 2 decimal places
            rounded = obj.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return f"{rounded:.2f}"  # Return as string to preserve .00
        except InvalidOperation:
            return None  # or "0.00"
    raise TypeError(f"Type {type(obj)} not serializable")