"""The quoting contract every storefront service prices against."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LineItem:
    name: str
    unit_price: float
    quantity: int

    @property
    def amount(self) -> float:
        return self.unit_price * self.quantity


DEFAULT_CURRENCY = "USD"


@dataclass(frozen=True)
class Quote:
    amount: float
    currency: str = DEFAULT_CURRENCY


def quote(
    items: list[LineItem],
    shipping: float = 0.0,
    discount_rate: float = 0.0,
    tax_rate: float = 0.0,
    currency: str = DEFAULT_CURRENCY,
) -> Quote:
    """Price a basket.

    Discounts apply to merchandise only; shipping joins afterwards and the whole
    payable amount is taxed. The quote is denominated in ``currency``, which the
    consumers render alongside the amount.
    """

    merchandise = sum(item.amount for item in items)
    payable = merchandise * (1 - discount_rate) + shipping
    payable = payable * (1 + tax_rate)
    return Quote(amount=round(payable, 2), currency=currency)
