from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from box_selection.models import Box, Product, Order, OrderItem


class APITests(APITestCase):
    """Integration and unit tests for the REST API and Dashboard views."""

    def setUp(self):
        # Create standard box and product
        self.box = Box.objects.create(
            name="API Box",
            width=Decimal("10.0"),
            height=Decimal("10.0"),
            depth=Decimal("10.0"),
            max_weight=Decimal("5.0"),
            cost=Decimal("1.50"),
            is_active=True,
        )
        self.product = Product.objects.create(
            sku="PROD-API",
            name="API Product",
            width=Decimal("5.0"),
            height=Decimal("5.0"),
            depth=Decimal("5.0"),
            weight=Decimal("1.0"),
        )
        self.order = Order.objects.create(
            order_number="ORD-API1",
            customer_name="API Customer",
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )

    def test_get_orders_list(self):
        """Verify GET /api/orders/ returns the expected response and structure."""
        url = reverse("api_order_list_create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be paginated list
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        orders = response.data["results"]
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["order_number"], "ORD-API1")
        self.assertEqual(orders[0]["customer_name"], "API Customer")

    def test_post_create_order_with_recommendation(self):
        """Verify POST /api/orders/ creates an order and computes a recommendation."""
        url = reverse("api_order_list_create")
        payload = {
            "order_number": "ORD-API2",
            "customer_name": "API Customer 2",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                }
            ],
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check order is created
        order = Order.objects.get(order_number="ORD-API2")
        self.assertEqual(order.customer_name, "API Customer 2")
        self.assertEqual(order.items.count(), 1)

        # Recommendation should be created because the view triggers update_recommendation
        self.assertTrue(hasattr(order, "recommendation"))
        self.assertEqual(order.recommendation.selected_box, self.box)
        self.assertEqual(order.status, Order.STATUS_PACKED)

        # Verify recommendation details in response
        self.assertIn("recommendation", response.data)
        self.assertEqual(response.data["recommendation"]["selected_box"]["id"], self.box.id)

    def test_post_create_order_invalid_payload(self):
        """Verify invalid requests return HTTP 400."""
        url = reverse("api_order_list_create")

        # Missing required customer_name
        payload_missing = {
            "order_number": "ORD-API-MISSING",
            "items": [],
        }
        response = self.client.post(url, payload_missing, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid nested product_id
        payload_invalid_product = {
            "order_number": "ORD-API-INVALID-PROD",
            "customer_name": "Invalid Customer",
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1,
                }
            ]
        }
        response = self.client.post(url, payload_invalid_product, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_detail(self):
        """Verify GET /api/orders/<id>/ returns order details."""
        url = reverse("api_order_detail", kwargs={"pk": self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)
        self.assertEqual(response.data["order_number"], "ORD-API1")

    def test_get_order_detail_non_existent(self):
        """Verify GET /api/orders/<id>/ returns HTTP 404 for non-existent order."""
        url = reverse("api_order_detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_recalculate_recommendation(self):
        """Verify POST /api/orders/<id>/recommend/ recalculates recommendations."""
        url = reverse("api_order_recommend", kwargs={"pk": self.order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("selected_box", response.data)
        self.assertEqual(response.data["selected_box"]["id"], self.box.id)

    def test_post_recalculate_recommendation_non_existent(self):
        """Verify POST /api/orders/<id>/recommend/ returns HTTP 404 for non-existent order."""
        url = reverse("api_order_recommend", kwargs={"pk": 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dashboard_get_renders_successfully(self):
        """Verify dashboard GET renders correctly with products, orders, and recommendation details."""
        url = reverse("order_dashboard")

        # Load dashboard without parameters
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Box Selection System")
        self.assertContains(response, "ORD-API1")

        # Load dashboard selecting the order
        url_with_param = f"{url}?order_id={self.order.id}"
        response_selected = self.client.get(url_with_param)
        self.assertEqual(response_selected.status_code, 200)
        self.assertContains(response_selected, "API Customer")
        self.assertContains(response_selected, "API Box")

    def test_dashboard_post_creates_orders(self):
        """Verify dashboard POST creates orders successfully."""
        url = reverse("order_dashboard")
        payload = {
            "order_number": "ORD-DASH-1",
            "customer_name": "Dash Customer 1",
            f"qty_{self.product.id}": "3",
        }
        response = self.client.post(url, payload)

        # Dashboard redirects on success to "/?order_id=<new_id>"
        self.assertEqual(response.status_code, 302)

        new_order = Order.objects.get(order_number="ORD-DASH-1")
        self.assertEqual(new_order.customer_name, "Dash Customer 1")
        self.assertEqual(new_order.items.first().quantity, 3)
        self.assertEqual(new_order.status, Order.STATUS_PACKED)
        self.assertIn(f"order_id={new_order.id}", response["Location"])

    def test_dashboard_post_rejects_duplicate_order_number(self):
        """Verify duplicate order numbers are rejected in dashboard."""
        url = reverse("order_dashboard")
        payload = {
            "order_number": "ORD-API1",  # Already exists from setUp
            "customer_name": "Another Customer",
            f"qty_{self.product.id}": "1",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)  # Renders the page with error
        self.assertContains(response, "already exists. Please use a different one.")
        self.assertFalse(Order.objects.filter(customer_name="Another Customer").exists())

    def test_dashboard_post_rejects_empty_items(self):
        """Verify orders without items are rejected in dashboard."""
        url = reverse("order_dashboard")
        payload = {
            "order_number": "ORD-DASH-NOITEMS",
            "customer_name": "No Items Customer",
            f"qty_{self.product.id}": "0",  # Zero quantity
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)  # Renders the page with error
        self.assertContains(response, "Please select at least one product with a quantity greater than zero.")
        self.assertFalse(Order.objects.filter(order_number="ORD-DASH-NOITEMS").exists())
