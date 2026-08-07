from django.contrib import admin, messages

from .models import Product, Box, Order, OrderItem, ShipmentRecommendation
from .services import update_recommendation


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class ShipmentRecommendationInline(admin.StackedInline):
    model = ShipmentRecommendation
    readonly_fields = (
        "selected_box",
        "volume_utilization",
        "weight_utilization",
        "cost",
        "packing_layout",
        "error_reason",
        "calculated_at",
    )
    can_delete = False
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "width", "height", "depth", "weight")
    search_fields = ("sku", "name")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("name", "width", "height", "depth", "max_weight", "cost", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "status", "created_at", "get_recommended_box")
    search_fields = ("order_number", "customer_name")
    list_filter = ("status",)
    inlines = [OrderItemInline, ShipmentRecommendationInline]
    actions = ["calculate_box_recommendation"]

    def get_recommended_box(self, obj):
        if hasattr(obj, "recommendation") and obj.recommendation.selected_box:
            return obj.recommendation.selected_box.name
        return "None"

    get_recommended_box.short_description = "Recommended Box"

    @admin.action(description="Calculate shipping box recommendation")
    def calculate_box_recommendation(self, request, queryset):
        success_count = sum(
            1 for order in queryset if update_recommendation(order)[1]["selected_box"]
        )
        failure_count = queryset.count() - success_count
        level = messages.SUCCESS if success_count else messages.WARNING
        self.message_user(
            request,
            f"{success_count} order(s) matched, {failure_count} could not be packed.",
            level,
        )
