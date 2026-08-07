from decimal import Decimal
from django.test import TestCase
from box_selection.models import Box, Product, Order, OrderItem
from box_selection.packing_solver import (
    does_overlap,
    _fits_by_dimensions,
    _orientations,
    _try_pack_box,
    solve_packing,
)


class PackingSolverTests(TestCase):
    """Tests for the 3D packing solver logic."""

    def test_does_overlap(self):
        """Test overlapping and non-overlapping placements in 3D space."""
        # Overlapping items
        item1 = {"x": 0, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}
        item2 = {"x": 5, "y": 5, "z": 5, "w": 10, "h": 10, "d": 10}
        self.assertTrue(does_overlap(item1, item2))

        # Non-overlapping (adjacent in x)
        item3 = {"x": 10, "y": 0, "z": 0, "w": 10, "h": 10, "d": 10}
        self.assertFalse(does_overlap(item1, item3))

        # Adjacent in y
        item4 = {"x": 0, "y": 10, "z": 0, "w": 10, "h": 10, "d": 10}
        self.assertFalse(does_overlap(item1, item4))

        # Adjacent in z
        item5 = {"x": 0, "y": 0, "z": 10, "w": 10, "h": 10, "d": 10}
        self.assertFalse(does_overlap(item1, item5))

    def test_fits_by_dimensions(self):
        """Test product dimensions vs box dimensions matching (including rotation)."""
        box = Box(width=Decimal("10.0"), height=Decimal("20.0"), depth=Decimal("30.0"))

        # Fits directly
        p1 = Product(width=Decimal("5.0"), height=Decimal("15.0"), depth=Decimal("25.0"))
        self.assertTrue(_fits_by_dimensions(p1, box))

        # Fits when rotated
        p2 = Product(width=Decimal("25.0"), height=Decimal("5.0"), depth=Decimal("15.0"))
        self.assertTrue(_fits_by_dimensions(p2, box))

        # Does not fit (one dimension too large)
        p3 = Product(width=Decimal("5.0"), height=Decimal("15.0"), depth=Decimal("35.0"))
        self.assertFalse(_fits_by_dimensions(p3, box))

    def test_orientations(self):
        """Test that all unique dimension permutations of a product are correctly returned."""
        p = Product(width=Decimal("10.0"), height=Decimal("20.0"), depth=Decimal("30.0"))
        orientations = _orientations(p)
        # Should return all unique permutations
        # 3 distinct dimensions -> 6 unique permutations
        self.assertEqual(len(orientations), 6)
        expected = sorted({
            (Decimal("10.0"), Decimal("20.0"), Decimal("30.0")),
            (Decimal("10.0"), Decimal("30.0"), Decimal("20.0")),
            (Decimal("20.0"), Decimal("10.0"), Decimal("30.0")),
            (Decimal("20.0"), Decimal("30.0"), Decimal("10.0")),
            (Decimal("30.0"), Decimal("10.0"), Decimal("20.0")),
            (Decimal("30.0"), Decimal("20.0"), Decimal("10.0")),
        }, key=lambda o: (o[1], o[0], o[2]))
        self.assertEqual(orientations, expected)

        # What if duplicate dimensions? E.g., a cube
        p_cube = Product(width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"))
        orientations_cube = _orientations(p_cube)
        self.assertEqual(len(orientations_cube), 1)
        self.assertEqual(orientations_cube, [(Decimal("10.0"), Decimal("10.0"), Decimal("10.0"))])

    def test_greedy_packing_no_overlap(self):
        """Verify the greedy packing algorithm places items without overlap."""
        box = Box(width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"))
        p1 = Product(sku="P1", name="Product 1", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"))
        p2 = Product(sku="P2", name="Product 2", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"))

        packed = _try_pack_box(box, [p1, p2])
        self.assertIsNotNone(packed)
        self.assertEqual(len(packed), 2)

        # Verify they don't overlap
        item1 = packed[0]
        item2 = packed[1]
        self.assertFalse(does_overlap(item1, item2))

    def test_solve_packing_empty_order(self):
        """Verify empty orders return the correct error."""
        order = Order.objects.create(order_number="ORD-EMPTY", customer_name="No Items")
        result = solve_packing(order)
        self.assertIsNone(result["selected_box"])
        self.assertEqual(result["error_reason"], "Order has no items.")

    def test_solve_packing_cheapest_valid_box(self):
        """Verify that the solver always selects the lowest-cost box capable of packing the order."""
        # Create active boxes with different costs
        # Box 1: small and cheap
        b1 = Box.objects.create(name="Small Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("5.0"), cost=Decimal("1.00"), is_active=True)
        # Box 2: medium and medium cost
        b2 = Box.objects.create(name="Medium Box", width=Decimal("20.0"), height=Decimal("20.0"), depth=Decimal("20.0"), max_weight=Decimal("15.0"), cost=Decimal("3.00"), is_active=True)
        # Box 3: large and expensive
        b3 = Box.objects.create(name="Large Box", width=Decimal("30.0"), height=Decimal("30.0"), depth=Decimal("30.0"), max_weight=Decimal("30.0"), cost=Decimal("5.00"), is_active=True)

        p = Product.objects.create(sku="P1", name="Product 1", width=Decimal("8.0"), height=Decimal("8.0"), depth=Decimal("8.0"), weight=Decimal("2.0"))
        order = Order.objects.create(order_number="ORD-CHEAP", customer_name="Test Customer")
        OrderItem.objects.create(order=order, product=p, quantity=1)

        result = solve_packing(order)
        self.assertEqual(result["selected_box"], b1)
        self.assertEqual(result["cost"], Decimal("1.00"))

    def test_solve_packing_weight_constraints(self):
        """Verify weight constraints filter out invalid boxes."""
        # Box fits dimensions but product is too heavy
        Box.objects.create(name="Light Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("1.0"), cost=Decimal("1.00"), is_active=True)
        b2 = Box.objects.create(name="Heavy Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("5.00"), is_active=True)

        p = Product.objects.create(sku="P1", name="Heavy Product", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"), weight=Decimal("5.0"))
        order = Order.objects.create(order_number="ORD-WEIGHT", customer_name="Heavy Customer")
        OrderItem.objects.create(order=order, product=p, quantity=1)

        result = solve_packing(order)
        self.assertEqual(result["selected_box"], b2)

    def test_solve_packing_dimension_constraints(self):
        """Verify dimension constraints filter out boxes too small for individual items."""
        Box.objects.create(name="Small Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("1.00"), is_active=True)
        p = Product.objects.create(sku="P1", name="Long Product", width=Decimal("12.0"), height=Decimal("5.0"), depth=Decimal("5.0"), weight=Decimal("1.0"))

        order = Order.objects.create(order_number="ORD-DIM", customer_name="Test Customer")
        OrderItem.objects.create(order=order, product=p, quantity=1)

        result = solve_packing(order)
        self.assertIsNone(result["selected_box"])
        self.assertIn("One or more items cannot fit", result["error_reason"])

    def test_solve_packing_inactive_boxes_ignored(self):
        """Verify inactive boxes are ignored by the solver."""
        Box.objects.create(name="Cheap Inactive", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("1.00"), is_active=False)
        b_expensive_active = Box.objects.create(name="Expensive Active", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("10.00"), is_active=True)

        p = Product.objects.create(sku="P1", name="Product", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"), weight=Decimal("1.0"))
        order = Order.objects.create(order_number="ORD-INACTIVE", customer_name="Test Customer")
        OrderItem.objects.create(order=order, product=p, quantity=1)

        result = solve_packing(order)
        self.assertEqual(result["selected_box"], b_expensive_active)

    def test_solve_packing_utilization_calculation(self):
        """Verify volume utilization and weight utilization are calculated correctly."""
        # 10x10x10 box (volume = 1000)
        # 5x5x5 product (volume = 125)
        # Volume utilization should be (125 / 1000) * 100 = 12.50%
        Box.objects.create(name="Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("1.00"), is_active=True)
        p = Product.objects.create(sku="P1", name="Product", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"), weight=Decimal("1.0"))
        order = Order.objects.create(order_number="ORD-UTIL", customer_name="Test Customer")
        OrderItem.objects.create(order=order, product=p, quantity=1)

        result = solve_packing(order)
        self.assertEqual(result["volume_utilization"], Decimal("12.50"))
        self.assertEqual(result["weight_utilization"], Decimal("12.50"))

    def test_solve_packing_layout_valid_coordinates(self):
        """Verify packing layout contains valid coordinates for every packed item."""
        b = Box.objects.create(name="Box", width=Decimal("10.0"), height=Decimal("10.0"), depth=Decimal("10.0"), max_weight=Decimal("10.0"), cost=Decimal("1.00"), is_active=True)
        p = Product.objects.create(sku="P1", name="Product", width=Decimal("5.0"), height=Decimal("5.0"), depth=Decimal("5.0"), weight=Decimal("1.0"))
        order = Order.objects.create(order_number="ORD-LAYOUT", customer_name="Test Customer")
        OrderItem.objects.create(order=order, product=p, quantity=2)

        result = solve_packing(order)
        layout = result["packing_layout"]
        self.assertEqual(len(layout), 2)
        for item in layout:
            self.assertEqual(item["sku"], "P1")
            self.assertEqual(item["name"], "Product")
            self.assertGreaterEqual(item["x"], 0)
            self.assertGreaterEqual(item["y"], 0)
            self.assertGreaterEqual(item["z"], 0)
            self.assertLessEqual(item["x"] + item["w"], b.width)
            self.assertLessEqual(item["y"] + item["h"], b.height)
            self.assertLessEqual(item["z"] + item["d"], b.depth)
