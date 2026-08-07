from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)

    width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Width in cm")
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Height in cm")
    depth = models.DecimalField(max_digits=8, decimal_places=2, help_text="Depth in cm")

    weight = models.DecimalField(max_digits=8, decimal_places=3, help_text="Weight in kg")

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def volume(self):
        return self.width * self.height * self.depth

    def clean(self):
        if self.width <= Decimal("0"):
            raise ValidationError({"width": "Width must be greater than zero."})

        if self.height <= Decimal("0"):
            raise ValidationError({"height": "Height must be greater than zero."})

        if self.depth <= Decimal("0"):
            raise ValidationError({"depth": "Depth must be greater than zero."})

        if self.weight <= Decimal("0"):
            raise ValidationError({"weight": "Weight must be greater than zero."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Box(models.Model):
    name = models.CharField(max_length=255)

    width = models.DecimalField(max_digits=8, decimal_places=2, help_text="Internal width in cm")
    height = models.DecimalField(max_digits=8, decimal_places=2, help_text="Internal height in cm")
    depth = models.DecimalField(max_digits=8, decimal_places=2, help_text="Internal depth in cm")

    max_weight = models.DecimalField(max_digits=8, decimal_places=3, help_text="Maximum weight capacity in kg")

    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost in USD")

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Boxes"

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.width}×{self.height}×{self.depth} cm, "
            f"max {self.max_weight} kg, ${self.cost})"
        )

    @property
    def volume(self):
        return self.width * self.height * self.depth

    def clean(self):
        if self.width <= Decimal("0"):
            raise ValidationError({"width": "Width must be greater than zero."})

        if self.height <= Decimal("0"):
            raise ValidationError({"height": "Height must be greater than zero."})

        if self.depth <= Decimal("0"):
            raise ValidationError({"depth": "Depth must be greater than zero."})

        if self.max_weight <= Decimal("0"):
            raise ValidationError({"max_weight": "Maximum weight must be greater than zero."})

        if self.cost < Decimal("0"):
            raise ValidationError({"cost": "Cost cannot be negative."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_PACKED = "Packed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PACKED, "Packed"),
    ]

    order_number = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.order_number}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be at least 1.")


class ShipmentRecommendation(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='recommendation')
    selected_box = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True, blank=True)
    volume_utilization = models.FloatField(null=True, blank=True, help_text="Volume utilization percentage")
    weight_utilization = models.FloatField(null=True, blank=True, help_text="Weight utilization percentage")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost of the selected box")
    packing_layout = models.JSONField(default=list, blank=True, help_text="List of placed items with coordinates and orientation")
    error_reason = models.TextField(blank=True, default="")
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.selected_box:
            return f"Recommendation for Order #{self.order.order_number}: {self.selected_box.name} (${self.cost})"
        return f"Recommendation for Order #{self.order.order_number}: No suitable box found"
