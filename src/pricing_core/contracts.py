"""Public pricing request and response contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LineItem:
    name: str
    unit_price: float
    quantity: int

    @property
    def amount(self) -> float:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Quote:
    amount: float
    currency: str = "USD"
    precision: int = 2
    merchandise: float = 0.0
    discount: float = 0.0
    shipping: float = 0.0
    tax: float = 0.0

    @property
    def subtotal(self) -> float:
        """Compatibility-friendly name for the merchandise total."""

        return self.merchandise

    @property
    def total(self) -> float:
        """Compatibility-friendly name for the final amount."""

        return self.amount

    @property
    def discount_amount(self) -> float:
        return self.discount

    @property
    def tax_amount(self) -> float:
        return self.tax
