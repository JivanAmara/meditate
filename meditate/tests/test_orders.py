from django.test import TestCase
from orders import unprocessed_order_report, send_alert

expectedReport = \
"""Orders to process:
---

ID: 1
Name:
PaymentMethod:        stripe
Total:                24.96
None


Items:

    (3) eBook, PDF
    (1) Paperback
---

"""

class TestUnprocessedOrderReport(TestCase):
    fixtures = ['tests/test_fixture.json']

    def test_report(self):
        r = unprocessed_order_report()
        self.assertEqual(r, expectedReport)

    def test_send_no_vars(self):
        r = unprocessed_order_report()
        with self.assertRaises(Exception):
            send_alert(r, send=True)
