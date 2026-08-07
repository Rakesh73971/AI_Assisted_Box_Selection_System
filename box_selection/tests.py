from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Product, Box, Order, OrderItem, ShipmentRecommendation
from .packing_solver import solve_packing, does_overlap

class ModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", sku="TEST-SKU",
            width=10.0, height=5.0, depth=2.0, weight=1.5
        )
        self.box = Box.objects.create(
            name="Test Box", width=20.0, height=15.0, depth=10.0,
            max_weight=5.0, cost=Decimal("1.50"), is_active=True
        )

    def test_product_volume_calculation(self):
        # 10 * 5 * 2 = 100
        self.assertEqual(self.product.volume, 100.0)

    def test_box_volume_calculation(self):
        # 20 * 15 * 10 = 3000
        self.assertEqual(self.box.volume, 3000.0)

    def test_product_validation(self):
        # Invalid dimensions should raise ValidationError on clean()
        invalid_product = Product(
            name="Invalid Product", sku="INVALID-SKU",
            width=-1.0, height=5.0, depth=2.0, weight=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_product.clean()

        invalid_product_weight = Product(
            name="Invalid Product Weight", sku="INVALID-SKU2",
            width=10.0, height=5.0, depth=2.0, weight=0
        )
        with self.assertRaises(ValidationError):
            invalid_product_weight.clean()

    def test_box_validation(self):
        invalid_box = Box(
            name="Invalid Box", width=20.0, height=15.0, depth=10.0,
            max_weight=-1.0, cost=Decimal("1.50")
        )
        with self.assertRaises(ValidationError):
            invalid_box.clean()

        invalid_box_cost = Box(
            name="Invalid Box Cost", width=20.0, height=15.0, depth=10.0,
            max_weight=5.0, cost=Decimal("-0.50")
        )
        with self.assertRaises(ValidationError):
            invalid_box_cost.clean()

    def test_invalid_product_save_is_rejected(self):
        invalid_product = Product(
            name="Invalid Product", sku="INVALID-SAVE",
            width=0.0, height=5.0, depth=2.0, weight=1.5
        )
        with self.assertRaises(ValidationError):
            invalid_product.save()


class SolverTests(TestCase):
    def setUp(self):
        # Create boxes with different dimensions, weight capacities, and costs
        self.small_box = Box.objects.create(
            name="Small Box", width=10.0, height=10.0, depth=10.0,
            max_weight=2.0, cost=Decimal("1.00"), is_active=True
        )
        self.medium_box = Box.objects.create(
            name="Medium Box", width=20.0, height=15.0, depth=15.0,
            max_weight=5.0, cost=Decimal("2.50"), is_active=True
        )
        self.large_box = Box.objects.create(
            name="Large Box", width=30.0, height=30.0, depth=30.0,
            max_weight=15.0, cost=Decimal("5.00"), is_active=True
        )
        
        # Products
        self.item_a = Product.objects.create(
            name="Item A", sku="ITEM-A", width=5.0, height=5.0, depth=5.0, weight=0.5
        )
        self.item_b = Product.objects.create(
            name="Item B", sku="ITEM-B", width=15.0, height=10.0, depth=10.0, weight=1.0
        )
        self.heavy_item = Product.objects.create(
            name="Heavy Item", sku="HEAVY", width=5.0, height=5.0, depth=5.0, weight=4.0
        )

    def test_cheapest_box_selection(self):
        # Item A (5x5x5, 0.5kg) fits in Small Box ($1.00)
        order = Order.objects.create(order_number="ORD-001", customer_name="Customer 1")
        OrderItem.objects.create(order=order, product=self.item_a, quantity=1)

        res = solve_packing(order)
        self.assertEqual(res['selected_box'], self.small_box)
        self.assertEqual(res['cost'], Decimal("1.00"))

    def test_selects_larger_box_when_dimensions_exceed(self):
        # Item B (15x10x10, 1.0kg) exceeds Small Box (10x10x10) but fits in Medium Box ($2.50)
        order = Order.objects.create(order_number="ORD-002", customer_name="Customer 2")
        OrderItem.objects.create(order=order, product=self.item_b, quantity=1)

        res = solve_packing(order)
        self.assertEqual(res['selected_box'], self.medium_box)
        self.assertEqual(res['cost'], Decimal("2.50"))

    def test_selects_larger_box_when_weight_exceeds(self):
        # Heavy Item (5x5x5, 4.0kg) fits in Small Box by size but exceeds its 2kg limit.
        # It must go in the Medium Box ($2.50) which supports up to 5kg.
        order = Order.objects.create(order_number="ORD-003", customer_name="Customer 3")
        OrderItem.objects.create(order=order, product=self.heavy_item, quantity=1)

        res = solve_packing(order)
        self.assertEqual(res['selected_box'], self.medium_box)
        self.assertEqual(res['cost'], Decimal("2.50"))

    def test_rejects_all_boxes_when_single_item_exceeds_all(self):
        # Huge item that exceeds all box dimensions
        huge_item = Product.objects.create(
            name="Huge", sku="HUGE", width=50.0, height=50.0, depth=50.0, weight=1.0
        )
        order = Order.objects.create(order_number="ORD-004", customer_name="Customer 4")
        OrderItem.objects.create(order=order, product=huge_item, quantity=1)

        res = solve_packing(order)
        self.assertIsNone(res["selected_box"])
        self.assertIn("cannot fit", res["error_reason"].lower())

    def test_rejects_all_boxes_when_weight_exceeds_all(self):
        # Weight exceeds all box capacities (15kg max)
        super_heavy = Product.objects.create(
            name="Super Heavy", sku="SHEAVY", width=5.0, height=5.0, depth=5.0, weight=20.0
        )
        order = Order.objects.create(order_number="ORD-005", customer_name="Customer 5")
        OrderItem.objects.create(order=order, product=super_heavy, quantity=1)

        res = solve_packing(order)
        self.assertIsNone(res["selected_box"])
        self.assertIn("exceeds", res["error_reason"].lower())

    def test_rotation_handling(self):
        # Box is 30x30x30, but let's test a box that is narrow but long: 30x10x10.
        # Item is 10x30x5. If rotated to 30x10x5, it will fit.
        flat_box = Box.objects.create(
            name="Flat Box", width=30.0, height=10.0, depth=10.0,
            max_weight=5.0, cost=Decimal("1.20"), is_active=True
        )
        item = Product.objects.create(
            name="Flat Item", sku="FLAT", width=10.0, height=30.0, depth=5.0, weight=1.0
        )
        order = Order.objects.create(order_number="ORD-006", customer_name="Customer 6")
        OrderItem.objects.create(order=order, product=item, quantity=1)

        # The Small Box (10x10x10) and Medium Box (20x15x15) cannot fit a length of 30cm.
        # Only flat_box (30x10x10, $1.20) or Large Box (30x30x30, $5.00) can fit it.
        # Since Flat Box is cheaper ($1.20), flat_box should be selected.
        res = solve_packing(order)
        self.assertEqual(res['selected_box'], flat_box)

    def test_non_overlapping_placements(self):
        # Put 8 Small items (5x5x5) into Medium Box (20x15x15).
        # Check that they pack without overlap.
        order = Order.objects.create(order_number="ORD-007", customer_name="Customer 7")
        OrderItem.objects.create(order=order, product=self.item_a, quantity=8)

        res = solve_packing(order)
        self.assertIsNotNone(res['selected_box'])
        
        layout = res['packing_layout']
        self.assertEqual(len(layout), 8)
        
        # Verify no two items overlap
        for i in range(len(layout)):
            for j in range(i + 1, len(layout)):
                item1 = layout[i]
                item2 = layout[j]
                self.assertFalse(does_overlap(item1, item2), f"Item {i} and {j} overlap!")

    def test_empty_order_returns_error(self):
        order = Order.objects.create(order_number="ORD-008", customer_name="Customer 8")
        res = solve_packing(order)
        self.assertIsNone(res['selected_box'])
        self.assertIn("no items", res['error_reason'].lower())

    def test_inactive_boxes_are_skipped(self):
        self.small_box.is_active = False
        self.small_box.save()
        order = Order.objects.create(order_number="ORD-009", customer_name="Customer 9")
        OrderItem.objects.create(order=order, product=self.item_a, quantity=1)

        res = solve_packing(order)
        # Should skip inactive small box and pick medium ($2.50) instead of small ($1.00)
        self.assertEqual(res['selected_box'], self.medium_box)


class APITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Cup", sku="CUP-1", width=8.0, height=8.0, depth=8.0, weight=0.3
        )
        self.box = Box.objects.create(
            name="Small Box", width=10.0, height=10.0, depth=10.0,
            max_weight=2.0, cost=Decimal("1.00"), is_active=True
        )

    def test_create_order_via_api(self):
        data = {
            "order_number": "ORD-API-001",
            "customer_name": "API Tester",
            "status": "Pending",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 1
                }
            ]
        }
        response = self.client.post('/api/orders/', data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['order_number'], "ORD-API-001")
        # Ensure recommendation was automatically calculated
        self.assertIsNotNone(response.json()['recommendation'])
        self.assertEqual(response.json()['recommendation']['selected_box']['name'], "Small Box")

    def test_get_order_details_api(self):
        order = Order.objects.create(order_number="ORD-API-002", customer_name="API Tester 2")
        OrderItem.objects.create(order=order, product=self.product, quantity=2)
        
        response = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['order_number'], "ORD-API-002")

    def test_rejects_zero_quantity_items(self):
        data = {
            "order_number": "ORD-API-004",
            "customer_name": "API Tester 4",
            "status": "Pending",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 0
                }
            ]
        }
        response = self.client.post('/api/orders/', data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.json()["items"][0])

    def test_recommend_endpoint_api(self):
        order = Order.objects.create(order_number="ORD-API-003", customer_name="API Tester 3")
        OrderItem.objects.create(order=order, product=self.product, quantity=1)

        # Trigger manually
        response = self.client.post(f'/api/orders/{order.id}/recommend/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['selected_box']['name'], "Small Box")
