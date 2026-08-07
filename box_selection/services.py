from django.db import transaction

from .models import Order, ShipmentRecommendation
from .packing_solver import solve_packing


@transaction.atomic
def update_recommendation(order: Order):
    """
    Calculate and persist the best shipping recommendation for an order.

    Returns:
        tuple[ShipmentRecommendation, dict]:
            The persisted recommendation and solver result.
    """
    result = solve_packing(order)

    recommendation, _ = ShipmentRecommendation.objects.update_or_create(
        order=order,
        defaults={
            key: value
            for key, value in {
                "selected_box": result["selected_box"],
                "volume_utilization": result["volume_utilization"],
                "weight_utilization": result["weight_utilization"],
                "cost": result["cost"],
                "packing_layout": result["packing_layout"],
                "error_reason": result["error_reason"] or "",
            }.items()
        },
    )

    order.status = (
        Order.STATUS_PACKED
        if recommendation.selected_box
        else Order.STATUS_PENDING
    )
    order.save(update_fields=["status"])

    return recommendation, result