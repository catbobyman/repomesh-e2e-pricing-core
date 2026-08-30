"""Currency metadata and monetary rounding rules."""

from decimal import Decimal, ROUND_HALF_UP
from types import MappingProxyType
from typing import Mapping


# This is the single source of truth for currencies accepted by pricing-core.
# The zero-decimal list follows ISO 4217's currently supported fund digits.
SUPPORTED_CURRENCY_PRECISION: Mapping[str, int] = MappingProxyType(
    {
        "USD": 2,
        "EUR": 2,
        "BIF": 0,
        "CLP": 0,
        "DJF": 0,
        "GNF": 0,
        "ISK": 0,
        "JPY": 0,
        "KMF": 0,
        "KRW": 0,
        "PYG": 0,
        "RWF": 0,
        "UGX": 0,
        "UYI": 0,
        "VND": 0,
        "VUV": 0,
        "XAF": 0,
        "XOF": 0,
        "XPF": 0,
    }
)
# Concise public alias; both names refer to the same immutable mapping.
CURRENCY_PRECISION = SUPPORTED_CURRENCY_PRECISION


def normalize_currency(currency: str) -> str:
    """Validate a supported ISO 4217 code and return its canonical form."""

    if not isinstance(currency, str):
        raise ValueError("currency must be a supported ISO 4217 code")
    normalized = currency.upper()
    if normalized not in SUPPORTED_CURRENCY_PRECISION:
        raise ValueError("currency must be a supported ISO 4217 code")
    return normalized


def currency_precision(currency: str) -> int:
    """Return the minor-unit precision for a validated currency."""

    return SUPPORTED_CURRENCY_PRECISION[normalize_currency(currency)]


get_precision = currency_precision


def round_money(value: float, precision: int) -> float:
    """Round a monetary value using decimal half-up semantics."""

    quantum = Decimal(1).scaleb(-precision)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))
