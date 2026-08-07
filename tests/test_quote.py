import unittest

from pricing_core import LineItem, quote


class QuoteAmountTests(unittest.TestCase):
    def test_merchandise_and_shipping(self) -> None:
        result = quote([LineItem("book", 10.0, 2)], shipping=5.0)
        self.assertEqual(result.amount, 25.0)

    def test_discount_applies_to_merchandise_only(self) -> None:
        result = quote([LineItem("book", 100.0, 1)], shipping=10.0, discount_rate=0.1)
        self.assertEqual(result.amount, 100.0)

    def test_tax_applies_to_the_payable_amount(self) -> None:
        result = quote(
            [LineItem("book", 100.0, 1)],
            shipping=10.0,
            discount_rate=0.1,
            tax_rate=0.1,
        )
        self.assertEqual(result.amount, 110.0)


class QuoteCurrencyTests(unittest.TestCase):
    """Multi-currency support: the contract consumers are waiting on."""

    def test_quote_reports_the_requested_currency(self) -> None:
        result = quote([LineItem("book", 10.0, 1)], currency="EUR")
        self.assertEqual(result.currency, "EUR")

    def test_quote_defaults_to_usd(self) -> None:
        result = quote([LineItem("book", 10.0, 1)])
        self.assertEqual(result.currency, "USD")


if __name__ == "__main__":
    unittest.main()
