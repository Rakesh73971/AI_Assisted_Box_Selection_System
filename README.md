# AI-Assisted Box Selection System

A Django application that recommends the most suitable shipping box for ecommerce orders. Given product dimensions/weight and available box catalog, the system selects the **cheapest box that can physically fit all items** while respecting weight limits.

## Problem Statement

When a customer places an order, warehouse staff need to know which shipping box to use. Each product has dimensions and weight; each box has internal dimensions, max weight capacity, and cost. This system automates that decision.

## Design Decisions

### Selection Strategy

1. **Expand order items** — Each `OrderItem.quantity` becomes individual packable units.
2. **Sort boxes by cost** — Cheapest active box is tried first (cost optimization).
3. **Pre-check constraints** — Total weight and per-item dimension bounds (with rotation) are validated before running the packing simulation.
4. **3D bin packing heuristic** — A greedy bottom-left-back placement algorithm tries all 6 orientations per item and tracks candidate anchor points to avoid overlap.
5. **Return first valid box** — Because boxes are sorted by cost, the first successful pack is the cheapest feasible option.

### Why a Heuristic (Not Exact Solver)?

Exact 3D bin packing is NP-hard. For a warehouse hiring assignment, a transparent greedy heuristic balances correctness, performance, and explainability. The solver returns:

- Selected box
- Volume and weight utilization %
- Full 3D placement coordinates per item
- Clear error reasons when no box fits

### Data Model

| Model                    | Purpose                                                       |
| ------------------------ | ------------------------------------------------------------- |
| `Product`                | Catalog item with W×H×D (cm) and weight (kg)                  |
| `Box`                    | Shipping container with internal dimensions, max weight, cost |
| `Order`                  | Customer order with status                                    |
| `OrderItem`              | Product + quantity on an order                                |
| `ShipmentRecommendation` | Cached packing result with layout JSON                        |

## Tech Stack

- Python 3.12+
- Django 5.2.x
- Django REST Framework 3.x
- SQLite (development)

## Setup

```bash
# Clone the repository
git clone <your-github-repo-url>
cd AI_Assisted_Box_Selection_System

# Create and activate a virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# (Optional) Load demo products, boxes, and a sample order
python manage.py seed_demo_data

# Create admin user (optional, for Django Admin)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Open:

- **Dashboard:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **API:** http://127.0.0.1:8000/api/

## Usage

### Web Dashboard

1. Add products and boxes via Django Admin (`/admin/`).
2. Create an order from the dashboard by entering order details and product quantities.
3. View the recommended box, utilization metrics, placement coordinates, and a top-down 2D packing visualization.

### REST API

| Method   | Endpoint                      | Description                                                      |
| -------- | ----------------------------- | ---------------------------------------------------------------- |
| GET/POST | `/api/products/`              | List or create products                                          |
| GET/POST | `/api/boxes/`                 | List or create boxes                                             |
| GET/POST | `/api/orders/`                | List or create orders (auto-calculates recommendation on create) |
| GET      | `/api/orders/<id>/`           | Get order details with recommendation                            |
| POST     | `/api/orders/<id>/recommend/` | Recalculate box recommendation                                   |

**Example: Create an order**

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-1001",
    "customer_name": "Jane Smith",
    "status": "Pending",
    "items": [{"product_id": 1, "quantity": 2}]
  }'
```

### Django Admin

- Manage products and boxes
- Create orders with inline order items
- Bulk action: **Calculate shipping box recommendation** on selected orders

## Running Tests

```bash
python manage.py test box_selection -v 2
```

See [TEST_OUTPUT.md](TEST_OUTPUT.md) for the latest test run output.

## Project Structure

```
AI_Assisted_Box_Selection_System/
├── box_selection/
│   ├── models.py              # Product, Box, Order, OrderItem, ShipmentRecommendation
│   ├── packing_solver.py      # 3D bin packing + box selection logic
│   ├── views.py               # REST API + dashboard view
│   ├── serializers.py         # DRF serializers
│   ├── admin.py               # Django Admin configuration
│   ├── tests/                 # Unit and integration test suites
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_solver.py
│   ├── management/commands/
│   │   └── seed_demo_data.py  # Demo data loader
│   └── templates/box_selection/dashboard.html
├── box_selection_project/     # Django project settings
├── .github/workflows/tests.yml
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── TEST_OUTPUT.md
└── LEARNINGS.md               # Your personal reflections (fill in yourself)
```

## Submission Checklist

- [x] README.md
- [x] AI_USAGE.md
- [x] Test cases (`box_selection/tests/`)
- [x] Test run output (`TEST_OUTPUT.md`)
- [x] GitHub Actions CI (`.github/workflows/tests.yml`)
- [ ] **GitHub repository link** — push this project to GitHub and add the URL
- [ ] **Chat transcript export** — export from Cursor manually (do not generate with AI)
- [ ] **LEARNINGS.md** — write your own reflections (do not use AI)

## Limitations

- The packing algorithm is heuristic; some valid packings may not be found.
- Items are treated as rigid rectangular boxes (no fragility or stacking rules).
- Only single-box shipments are supported (no multi-box splitting).

## License

Submitted as a hiring assignment project.
