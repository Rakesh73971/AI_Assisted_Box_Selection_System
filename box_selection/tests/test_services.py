from decimal import Decimal
from django.test import TestCase
from box_selection.models import Box, Product, Order, OrderItem, ShipmentRecommendation
from box_selection.services import update_recommendation


class ServiceTests(TestCase):
    """Tests for the service layer logic, specifically recommendation calculation and persistence."""

    def setUp(self):
        # Create standard test box and product
        self.box = Box.objects.create(
            name="Service Box",
            width=Decimal("10.0"),
            height=Decimal("10.0"),
            depth=Decimal("10.0"),
            max_weight=Decimal("5.0"),
            cost=Decimal("1.50"),
            is_active=True,
        )
        self.product = Product.objects.create(
            sku="PROD-S",
            name="Service Product",
            width=Decimal("5.0"),
            height=Decimal("5.0"),
            depth=Decimal("5.0"),
            weight=Decimal("1.0"),
        )
        self.order = Order.objects.create(
            order_number="ORD-S1",
            customer_name="Service Customer",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )

    def test_recommendation_created_successfully(self):
        """Verify recommendations are created successfully."""
        # Before calling service, there should be no ShipmentRecommendation
        self.assertFalse(ShipmentRecommendation.objects.filter(order=self.order).exists())

        recommendation, result = update_recommendation(self.order)

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.order, self.order)
        self.assertEqual(recommendation.selected_box, self.box)
        self.assertTrue(ShipmentRecommendation.objects.filter(order=self.order).exists())

    def test_existing_recommendation_updated(self):
        """Verify existing recommendations are updated."""
        # Create an initial recommendation by calling service
        rec1, _ = update_recommendation(self.order)
        self.assertEqual(rec1.cost, Decimal("1.50"))

        # Now change the box cost to check if recommendation is updated
        self.box.cost = Decimal("2.99")
        self.box.save()

        rec2, _ = update_recommendation(self.order)
        self.assertEqual(rec2.id, rec1.id)  # Same instance updated
        self.assertEqual(rec2.cost, Decimal("2.99"))

    def test_order_status_changes_to_packed(self):
        """Verify order status changes to Packed."""
        self.assertEqual(self.order.status, Order.STATUS_PENDING)

        update_recommendation(self.order)

        # Refresh from db
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PACKED)

    def test_pending_status_retained_when_no_box_fits(self):
        """Verify Pending status is retained when no box fits."""
        # Create a new order with a product that is too large for the box
        large_product = Product.objects.create(
            sku="PROD-L",
            name="Large Product",
            width=Decimal("50.0"),
            height=Decimal("50.0"),
            depth=Decimal("50.0"),
            weight=Decimal("1.0"),
        )
        order2 = Order.objects.create(
            order_number="ORD-S2",
            customer_name="Service Customer 2",
        )
        OrderItem.objects.create(
            order=order2,
            product=large_product,
            quantity=1,
        )

        recommendation, result = update_recommendation(order2)

        self.assertIsNone(recommendation.selected_box)
        order2.refresh_from_db()
        self.assertEqual(order2.status, Order.STATUS_PENDING)

    def test_data_persisted_correctly(self):
        """Verify packing layout, utilization values, and error messages are persisted correctly."""
        # Call service
        rec, _ = update_recommendation(self.order)

        # Retrieve from db
        persisted = ShipmentRecommendation.objects.get(id=rec.id)
        self.assertEqual(persisted.volume_utilization, 12.5)
        self.assertEqual(persisted.weight_utilization, 12.5)
        self.assertEqual(persisted.cost, Decimal("1.50"))
        self.assertEqual(persisted.error_reason, "")
        self.assertEqual(len(persisted.packing_layout), 1)
        layout_item = persisted.packing_layout[0]
        self.assertEqual(layout_item["sku"], "PROD-S")

        # Now test persistence of error message when it fails
        large_product = Product.objects.create(
            sku="PROD-L",
            name="Large Product",
            width=Decimal("50.0"),
            height=Decimal("50.0"),
            depth=Decimal("50.0"),
            weight=Decimal("1.0"),
        )
        order2 = Order.objects.create(
            order_number="ORD-S3",
            customer_name="Service Customer 3",
        )
        OrderItem.objects.create(
            order=order2,
            product=large_product,
            quantity=1,
        )

        rec2, _ = update_recommendation(order2)
        persisted2 = ShipmentRecommendation.objects.get(id=rec2.id)
        self.assertIn("One or more items cannot fit", persisted2.error_reason)
