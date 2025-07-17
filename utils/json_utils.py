from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def decimal_default(obj):
    if isinstance(obj, Decimal):
        try:
            quantized = obj.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # Force two decimal places in string format (e.g. "10.00")
            return f"{quantized:.2f}"
        except InvalidOperation:
            return None  # or "NaN", or raise error
    raise TypeError(f"Type {type(obj)} not serializable")
