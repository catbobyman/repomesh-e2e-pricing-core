import unittest

from pricing_core import ZERO_DECIMAL_CURRENCIES, LineItem, quote


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

    def test_line_items_default_to_usd(self) -> None:
        self.assertEqual(LineItem("book", 10.0, 1).currency, "USD")

    def test_line_items_are_repriced_into_the_quote_currency(self) -> None:
        line = LineItem("book", 10.0, 1).in_currency("EUR")
        self.assertEqual(line.currency, "EUR")


class ZeroDecimalRoundingTests(unittest.TestCase):
    """JPY, KRW and VND have no minor unit: every amount is a whole number."""

    def test_the_quote_total_is_a_whole_number(self) -> None:
        for currency in sorted(ZERO_DECIMAL_CURRENCIES):
            with self.subTest(currency=currency):
                result = quote([LineItem("desk", 199.99, 1)], currency=currency)
                self.assertEqual(result.amount, 200.0)

    def test_unit_prices_are_rounded_to_whole_units(self) -> None:
        line = LineItem("desk", 199.99, 1, "JPY")
        self.assertEqual(line.unit_price, 200.0)

    def test_line_totals_are_rounded_before_they_are_summed(self) -> None:
        # Rounding each line first gives 49 * 3 + 0; summing raw prices first
        # would give 148.6 and round up to 149.
        result = quote(
            [LineItem("lamp", 49.4, 3), LineItem("pen", 0.4, 1)],
            currency="JPY",
        )
        self.assertEqual(result.amount, 147.0)

    def test_shipping_tax_and_discount_stay_whole(self) -> None:
        result = quote(
            [LineItem("desk", 199.99, 1)],
            shipping=20.4,
            discount_rate=0.1,
            tax_rate=0.08,
            currency="JPY",
        )
        self.assertEqual(result.amount, 216.0)

    def test_decimal_currencies_keep_their_minor_unit(self) -> None:
        result = quote([LineItem("desk", 199.99, 1)], currency="EUR")
        self.assertEqual(result.amount, 199.99)


if __name__ == "__main__":
    unittest.main()
