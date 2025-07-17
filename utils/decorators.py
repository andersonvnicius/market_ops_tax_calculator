from decimal import Decimal, ROUND_HALF_UP
from functools import wraps

def round_decimal_output(places: str = "0.01"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            if isinstance(result, Decimal):
                return result.quantize(Decimal(places), rounding=ROUND_HALF_UP)
            return result  # fallback if not Decimal
        return wrapper
    return decorator
