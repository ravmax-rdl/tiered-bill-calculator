import unittest

from tiered_bill_calculator.bill import calculate_bill


class TestTieredBillCalculator(unittest.TestCase):
    def test_low_tier_k_30(self) -> None:
        r = calculate_bill(0, 30)
        self.assertEqual(r.tier, "low")
        self.assertEqual(r.value, r.total - 800)
        self.assertEqual(r.value, 150)
        self.assertEqual(r.total, 950)

    def test_normal_tier_k_60(self) -> None:
        r = calculate_bill(0, 60)
        self.assertEqual(r.tier, "normal")
        self.assertEqual(r.value, 450)
        self.assertEqual(r.total, 1250)

    def test_high_tier_k_90(self) -> None:
        r = calculate_bill(0, 90)
        self.assertEqual(r.tier, "high")
        self.assertEqual(r.value, 1050)
        self.assertEqual(r.total, 1850)

    def test_very_high_tier_k_100(self) -> None:
        r = calculate_bill(0, 100)
        self.assertEqual(r.tier, "very high")
        self.assertEqual(r.value, 1350)
        self.assertEqual(r.total, 2150)

    def test_invalid_when_current_less_than_previous(self) -> None:
        with self.assertRaises(ValueError):
            calculate_bill(10, 5)


if __name__ == "__main__":
    unittest.main()

