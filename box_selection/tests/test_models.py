from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from box_selection.models import Box, Product


class ProductModelTests(TestCase):
    """Tests for the Product model."""

    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="Test Product",
            sku="TEST-SKU",
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            depth=Decimal("2.00"),
            weight=Decimal("1.500"),
        )

    def test_product_volume_calculation(self):
        """Product volume should be width × height × depth."""
        self.assertEqual(
            self.product.volume,
            Decimal("100.0000")
        )

    def test_valid_product_is_saved(self):
        """A valid product should be saved successfully."""
        self.assertEqual(Product.objects.count(), 1)

    def test_negative_dimension_validation(self):
        """Negative dimensions should raise ValidationError."""
        product = Product(
            name="Invalid Product",
            sku="INVALID-1",
            width=Decimal("-1.00"),
            height=Decimal("5.00"),
            depth=Decimal("2.00"),
            weight=Decimal("1.000"),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_zero_dimension_validation(self):
        """Zero dimensions should raise ValidationError."""
        product = Product(
            name="Invalid Product",
            sku="INVALID-2",
            width=Decimal("0.00"),
            height=Decimal("5.00"),
            depth=Decimal("2.00"),
            weight=Decimal("1.000"),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_zero_weight_validation(self):
        """Weight must be greater than zero."""
        product = Product(
            name="Invalid Product",
            sku="INVALID-3",
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            depth=Decimal("2.00"),
            weight=Decimal("0.000"),
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_string_representation(self):
        """__str__ should return name and SKU."""
        self.assertEqual(
            str(self.product),
            "Test Product (TEST-SKU)"
        )


class BoxModelTests(TestCase):
    """Tests for the Box model."""

    @classmethod
    def setUpTestData(cls):
        cls.box = Box.objects.create(
            name="Medium Box",
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            depth=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("1.50"),
            is_active=True,
        )

    def test_box_volume_calculation(self):
        """Box volume should be width × height × depth."""
        self.assertEqual(
            self.box.volume,
            Decimal("3000.0000")
        )

    def test_valid_box_is_saved(self):
        """A valid box should be saved successfully."""
        self.assertEqual(Box.objects.count(), 1)

    def test_negative_dimension_validation(self):
        """Negative dimensions should not be allowed."""
        box = Box(
            name="Invalid Box",
            width=Decimal("-20.00"),
            height=Decimal("15.00"),
            depth=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("1.00"),
        )

        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_zero_max_weight_validation(self):
        """Maximum weight must be greater than zero."""
        box = Box(
            name="Invalid Box",
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            depth=Decimal("10.00"),
            max_weight=Decimal("0.000"),
            cost=Decimal("1.00"),
        )

        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_negative_cost_validation(self):
        """Cost cannot be negative."""
        box = Box(
            name="Invalid Box",
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            depth=Decimal("10.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_box_string_representation(self):
        """__str__ should include box details."""
        self.assertIn("Medium Box", str(self.box))
        self.assertIn("20.00", str(self.box))