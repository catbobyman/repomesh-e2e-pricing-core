"""Shared quoting contract for the storefront."""

from .contracts import LineItem, Quote
from .quote import quote
from .rounding import (
    CURRENCY_PRECISION,
    SUPPORTED_CURRENCY_PRECISION,
    currency_precision,
    get_precision,
    normalize_currency,
    round_money,
)

__all__ = [
    "LineItem",
    "Quote",
    "CURRENCY_PRECISION",
    "SUPPORTED_CURRENCY_PRECISION",
    "currency_precision",
    "get_precision",
    "normalize_currency",
    "quote",
    "round_money",
]
