from decimal import Decimal

from django.core.management.base import BaseCommand

from box_selection.models import Box, Order, OrderItem, Product
from box_selection.services import update_recommendation


class Command(BaseCommand):
    help = "Load sample products, boxes, and a demo order."

    def handle(self, *args, **options):
        for data in [
            {"name": "Wireless Mouse", "sku": "MOUSE-001", "width": 8.0, "height": 4.0, "depth": 12.0, "weight": 0.2},
            {"name": "Mechanical Keyboard", "sku": "KB-001", "width": 45.0, "height": 5.0, "depth": 15.0, "weight": 1.1},
            {"name": "USB-C Hub", "sku": "HUB-001", "width": 10.0, "height": 2.0, "depth": 6.0, "weight": 0.15},
        ]:
            Product.objects.update_or_create(sku=data["sku"], defaults=data)

        for data in [
            {"name": "Small Mailer", "width": 15.0, "height": 10.0, "depth": 10.0, "max_weight": 2.0, "cost": Decimal("1.25")},
            {"name": "Medium Carton", "width": 30.0, "height": 20.0, "depth": 15.0, "max_weight": 8.0, "cost": Decimal("2.75")},
            {"name": "Large Carton", "width": 45.0, "height": 30.0, "depth": 25.0, "max_weight": 20.0, "cost": Decimal("4.50")},
        ]:
            Box.objects.update_or_create(name=data["name"], defaults={**data, "is_active": True})

        order, created = Order.objects.get_or_create(
            order_number="DEMO-1001",
            defaults={"customer_name": "Demo Customer"},
        )
        if created:
            OrderItem.objects.create(order=order, product=Product.objects.get(sku="MOUSE-001"), quantity=2)
            OrderItem.objects.create(order=order, product=Product.objects.get(sku="HUB-001"), quantity=1)
            OrderItem.objects.create(order=order, product=Product.objects.get(sku="KB-001"), quantity=1)

        recommendation, _ = update_recommendation(order)
        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
        if recommendation.selected_box:
            self.stdout.write(f"DEMO-1001 -> {recommendation.selected_box.name} (${recommendation.cost})")
