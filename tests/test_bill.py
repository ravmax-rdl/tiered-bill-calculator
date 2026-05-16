import unittest

from tiered_bill_calculator.bill import calculate_bill, parse_reading


class TestTieredBillCalculator(unittest.TestCase):
    def test_low_tier_k_30(self) -> None:
        r = calculate_bill(0, 30)
        self.assertEqual(r.tier, "low")
        self.assertEqual(r.fixed_fee, 200)
        self.assertEqual(r.value, 150)
        self.assertEqual(r.total, 350)

    def test_normal_tier_k_60(self) -> None:
        r = calculate_bill(0, 60)
        self.assertEqual(r.tier, "normal")
        self.assertEqual(r.fixed_fee, 400)
        self.assertEqual(r.value, 450)
        self.assertEqual(r.total, 850)

    def test_high_tier_k_90(self) -> None:
        r = calculate_bill(0, 90)
        self.assertEqual(r.tier, "high")
        self.assertEqual(r.fixed_fee, 600)
        self.assertEqual(r.value, 1050)
        self.assertEqual(r.total, 1650)

    def test_very_high_tier_k_100(self) -> None:
        r = calculate_bill(0, 100)
        self.assertEqual(r.tier, "very high")
        self.assertEqual(r.fixed_fee, 800)
        self.assertEqual(r.value, 1350)
        self.assertEqual(r.total, 2150)

    def test_invalid_when_current_less_than_previous(self) -> None:
        with self.assertRaises(ValueError):
            calculate_bill(10, 5)

    def test_negative_previous_reading_raises(self) -> None:
        with self.assertRaises(ValueError):
            calculate_bill(-1, 50)

    def test_negative_current_reading_raises(self) -> None:
        with self.assertRaises(ValueError):
            calculate_bill(0, -10)

    def test_decimal_reading_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading("45.5")

    def test_integer_reading_accepted(self) -> None:
        self.assertEqual(int(parse_reading("45")), 45)


if __name__ == "__main__":
    unittest.main()
