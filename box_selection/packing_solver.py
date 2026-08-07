from decimal import Decimal
from itertools import permutations

from .models import Box


def does_overlap(item1, item2):
    return (
        item1["x"] < item2["x"] + item2["w"] and item1["x"] + item1["w"] > item2["x"]
        and item1["y"] < item2["y"] + item2["h"] and item1["y"] + item1["h"] > item2["y"]
        and item1["z"] < item2["z"] + item2["d"] and item1["z"] + item1["d"] > item2["z"]
    )


def _fits_by_dimensions(product, box):
    product_dims = sorted([product.width, product.height, product.depth])
    box_dims = sorted([box.width, box.height, box.depth])
    return all(p <= b for p, b in zip(product_dims, box_dims))


def _orientations(product):
    dims = (product.width, product.height, product.depth)
    return sorted(set(permutations(dims)), key=lambda o: (o[1], o[0], o[2]))


def _try_pack_box(box, flat_items):
    packed_items = []
    candidates = [(0.0, 0.0, 0.0)]

    for product in flat_items:
        placed = False
        valid_candidates = sorted(
            {c for c in candidates if c[0] < box.width and c[1] < box.height and c[2] < box.depth},
            key=lambda c: (c[1], c[2], c[0]),
        )

        for cx, cy, cz in valid_candidates:
            for w, h, d in _orientations(product):
                if cx + w > box.width or cy + h > box.height or cz + d > box.depth:
                    continue
                test_item = {"x": cx, "y": cy, "z": cz, "w": w, "h": h, "d": d}
                if any(does_overlap(test_item, packed) for packed in packed_items):
                    continue
                packed_items.append({
                    "sku": product.sku,
                    "name": product.name,
                    "x": cx, "y": cy, "z": cz,
                    "w": w, "h": h, "d": d,
                })
                candidates.extend([(cx + w, cy, cz), (cx, cy + h, cz), (cx, cy, cz + d)])
                candidates.remove((cx, cy, cz))
                placed = True
                break
            if placed:
                break

        if not placed:
            return None

    return packed_items


def solve_packing(order):
    flat_items = []
    total_weight = 0.0
    total_item_volume = 0.0

    for item in order.items.select_related("product"):
        for _ in range(item.quantity):
            flat_items.append(item.product)
            total_weight += item.product.weight
            total_item_volume += item.product.volume

    if not flat_items:
        return {
            "selected_box": None,
            "volume_utilization": 0.0,
            "weight_utilization": 0.0,
            "cost": Decimal("0.00"),
            "packing_layout": [],
            "error_reason": "Order has no items.",
        }

    flat_items.sort(key=lambda p: (p.volume, p.weight), reverse=True)
    last_error = "No suitable box found."

    for box in Box.objects.filter(is_active=True).order_by("cost", "width", "height", "depth"):
        if total_weight > box.max_weight:
            last_error = f"Total weight ({total_weight:.2f} kg) exceeds '{box.name}' capacity ({box.max_weight:.2f} kg)."
            continue

        if not all(_fits_by_dimensions(product, box) for product in flat_items):
            last_error = f"One or more items cannot fit in '{box.name}'."
            continue

        packed_items = _try_pack_box(box, flat_items)
        if packed_items is None:
            last_error = f"'{box.name}' could not pack all items."
            continue

        return {
            "selected_box": box,
            "volume_utilization": round((total_item_volume / box.volume) * 100.0, 2),
            "weight_utilization": round((total_weight / box.max_weight) * 100.0, 2),
            "cost": box.cost,
            "packing_layout": packed_items,
            "error_reason": None,
        }

    return {
        "selected_box": None,
        "volume_utilization": 0.0,
        "weight_utilization": 0.0,
        "cost": Decimal("0.00"),
        "packing_layout": [],
        "error_reason": last_error,
    }
