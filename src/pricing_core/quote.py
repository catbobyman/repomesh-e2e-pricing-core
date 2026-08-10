"""The quoting contract every storefront service prices against."""

from dataclasses import dataclass, replace

DEFAULT_CURRENCY = "USD"

#: ISO 4217 currencies without a minor unit: every amount is a whole number.
ZERO_DECIMAL_CURRENCIES = frozenset({"JPY", "KRW", "VND"})


def normalize_currency(currency: str) -> str:
    """The canonical ISO 4217 spelling, falling back to the default currency."""

    return (currency or DEFAULT_CURRENCY).strip().upper()


def minor_units(currency: str) -> int:
    """Decimal places the currency's minor unit allows."""

    return 0 if normalize_currency(currency) in ZERO_DECIMAL_CURRENCIES else 2


def round_amount(amount: float, currency: str) -> float:
    """Round a monetary amount to the precision its currency allows.

    Zero-decimal currencies land on whole units; everything else keeps cents.
    Every monetary value in this module passes through here, so a quote never
    reports a fraction the currency cannot express.
    """

    return round(amount, minor_units(currency))


@dataclass(frozen=True)
class LineItem:
    name: str
    unit_price: float
    quantity: int
    currency: str = DEFAULT_CURRENCY

    def __post_init__(self) -> None:
        currency = normalize_currency(self.currency)
        object.__setattr__(self, "currency", currency)
        object.__setattr__(self, "unit_price", round_amount(self.unit_price, currency))

    @property
    def amount(self) -> float:
        return round_amount(self.unit_price * self.quantity, self.currency)

    def in_currency(self, currency: str) -> "LineItem":
        """This line priced in ``currency``, re-rounded to that currency."""

        currency = normalize_currency(currency)
        if currency == self.currency:
            return self
        return replace(self, currency=currency)


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
    """Price a basket in ``currency`` (ISO 4217).

    Discounts apply to merchandise only; shipping joins afterwards and the whole
    payable amount is taxed. Every step is rounded to the currency's precision,
    so a zero-decimal currency such as JPY never carries a fractional unit.
    """

    currency = normalize_currency(currency)
    priced = [item.in_currency(currency) for item in items]

    merchandise = round_amount(sum(item.amount for item in priced), currency)
    payable = round_amount(
        merchandise * (1 - discount_rate) + round_amount(shipping, currency), currency
    )
    payable = round_amount(payable * (1 + tax_rate), currency)
    return Quote(amount=payable, currency=currency)
