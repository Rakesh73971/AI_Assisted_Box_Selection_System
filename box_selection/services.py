from .models import Order, ShipmentRecommendation
from .packing_solver import solve_packing


def update_recommendation(order):
    """Run the packing solver and persist the result for an order."""
    result = solve_packing(order)
    recommendation, _ = ShipmentRecommendation.objects.update_or_create(
        order=order,
        defaults={
            "selected_box": result["selected_box"],
            "volume_utilization": result["volume_utilization"],
            "weight_utilization": result["weight_utilization"],
            "cost": result["cost"],
            "packing_layout": result["packing_layout"],
            "error_reason": result["error_reason"] or "",
        },
    )

    new_status = "Packed" if result["selected_box"] else "Pending"
    if order.status != new_status:
        order.status = new_status
        order.save(update_fields=["status"])

    return recommendation, result