"""Cross-repository joint test for the multi-currency contract.

Unlike each repository's own suite, this one imports the *real* implementations
of all three repositories at their candidate revisions. A consumer that ignores
the currency, or a producer that never accepted one, fails here even though every
single-repository CI is green.
"""

import unittest

from billing.invoice import render_invoice
from checkout.order import order_summary
from pricing_core import LineItem


class MultiCurrencyFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.basket = [LineItem("desk", 200.0, 1), LineItem("lamp", 50.0, 2)]

    def test_order_summary_carries_the_requested_currency(self) -> None:
        summary = order_summary(self.basket, shipping=20.0, currency="EUR")
        self.assertEqual(summary["currency"], "EUR")

    def test_invoice_matches_the_order_currency(self) -> None:
        summary = order_summary(self.basket, shipping=20.0, currency="EUR")
        invoice = render_invoice(self.basket, shipping=20.0, currency="EUR")
        self.assertEqual(invoice["currency"], summary["currency"])
        self.assertEqual(invoice["amount_due"], summary["total"])

    def test_zero_decimal_currency_is_rounded_to_whole_units(self) -> None:
        """JPY has no minor unit, so the payable amount must be a whole number.

        No repository's own suite can see this rule: the consumers price against
        the contract stub, which is deliberately silent about rounding, and the
        producer's suite only covers the currency it was asked for. The rule is a
        property of the assembled system, so only a joint test can enforce it.
        """

        basket = [LineItem("desk", 199.99, 1)]
        self.assertEqual(order_summary(basket, currency="JPY")["total"], 200.0)
        self.assertEqual(render_invoice(basket, currency="JPY")["amount_due"], 200.0)

    def test_every_supported_currency_flows_end_to_end(self) -> None:
        for currency in ("USD", "EUR", "JPY"):
            with self.subTest(currency=currency):
                summary = order_summary(self.basket, currency=currency)
                invoice = render_invoice(self.basket, currency=currency)
                self.assertEqual(summary["currency"], currency)
                self.assertEqual(invoice["currency"], currency)


if __name__ == "__main__":
    unittest.main()
