"""The quoting contract every storefront service prices against."""

from .contracts import LineItem, Quote
from .rounding import currency_precision, normalize_currency, round_money


def quote(
    items: list[LineItem],
    shipping: float = 0.0,
    discount_rate: float = 0.0,
    tax_rate: float = 0.0,
    currency: str = "USD",
) -> Quote:
    """Price a basket.

    Discounts apply to merchandise only; shipping joins afterwards and the whole
    payable amount is taxed.
    """

    normalized_currency = normalize_currency(currency)
    precision = currency_precision(normalized_currency)
    merchandise = sum(item.amount for item in items)
    discount = merchandise * discount_rate
    taxable = merchandise - discount + shipping
    tax = taxable * tax_rate
    payable = taxable + tax
    return Quote(
        amount=round_money(payable, precision),
        currency=normalized_currency,
        precision=precision,
        merchandise=round_money(merchandise, precision),
        discount=round_money(discount, precision),
        shipping=round_money(shipping, precision),
        tax=round_money(tax, precision),
    )
