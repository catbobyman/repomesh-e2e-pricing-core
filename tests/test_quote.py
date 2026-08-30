import unittest

from pricing_core import LineItem, SUPPORTED_CURRENCY_PRECISION, quote, round_money
from pricing_core.api import route_request


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

    def test_currency_is_normalized_and_reports_precision(self) -> None:
        result = quote([LineItem("book", 10.0, 1)], currency="eur")
        self.assertEqual((result.currency, result.precision), ("EUR", 2))

    def test_invalid_currency_is_rejected(self) -> None:
        for currency in ("GBP", "US", " usd", None):
            with self.subTest(currency=currency), self.assertRaises(ValueError):
                quote([], currency=currency)  # type: ignore[arg-type]


class QuoteRoundingTests(unittest.TestCase):
    def test_half_boundaries_round_away_from_zero(self) -> None:
        self.assertEqual(round_money(1.005, 2), 1.01)
        self.assertEqual(round_money(199.5, 0), 200.0)
        self.assertEqual(round_money(-1.005, 2), -1.01)

    def test_every_monetary_field_uses_currency_precision(self) -> None:
        result = quote(
            [LineItem("desk", 199.6, 1)],
            shipping=1.6,
            discount_rate=0.015,
            tax_rate=0.075,
            currency="JPY",
        )
        self.assertEqual(result.precision, 0)
        for field in ("amount", "merchandise", "discount", "shipping", "tax"):
            with self.subTest(field=field):
                self.assertEqual(getattr(result, field) % 1, 0)

    def test_supported_currency_metadata_is_authoritative(self) -> None:
        self.assertEqual(SUPPORTED_CURRENCY_PRECISION["USD"], 2)
        self.assertEqual(SUPPORTED_CURRENCY_PRECISION["EUR"], 2)
        for currency in ("JPY", "KRW", "VND"):
            self.assertEqual(SUPPORTED_CURRENCY_PRECISION[currency], 0)


class PricingApiTests(unittest.TestCase):
    def test_quote_endpoint_preserves_amount_and_adds_metadata(self) -> None:
        status, body = route_request(
            "POST", "/quote", {"items": [{"name": "book", "unit_price": 1.005, "quantity": 1}], "currency": "eur"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["amount"], 1.01)
        self.assertEqual((body["currency"], body["precision"]), ("EUR", 2))

    def test_quote_endpoint_uses_existing_error_shape(self) -> None:
        status, body = route_request("POST", "/quote", {"currency": "GBP"})
        self.assertEqual(status, 400)
        self.assertEqual(set(body), {"error"})

    def test_rounding_rules_endpoint_exposes_authoritative_mapping(self) -> None:
        status, body = route_request("GET", "/pricing/rounding-rules")
        self.assertEqual(status, 200)
        self.assertEqual(body, dict(SUPPORTED_CURRENCY_PRECISION))


if __name__ == "__main__":
    unittest.main()
