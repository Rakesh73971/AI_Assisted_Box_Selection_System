# AI-Assisted Box Selection System

A Django-based application that recommends the most cost-effective shipping box for an order based on product dimensions, weight, and available box sizes.

The system automatically determines whether all items can fit inside a single box while respecting weight limits and returns the cheapest valid option.

---

## Features

- Product, Box, Order, and Shipment Recommendation management
- Automatic shipping box recommendation
- 3D greedy packing with item rotation support
- Weight and dimension validation
- Django Admin for data management
- REST API built with Django REST Framework
- Web dashboard for creating orders and viewing recommendations
- Pagination for API endpoints
- Unit and integration tests using Pytest

---

## How It Works

When an order is created, the application:

1. Expands each order item based on its quantity.
2. Calculates the total weight.
3. Sorts active boxes by cost.
4. Checks whether every product can fit inside each box (rotation supported).
5. Attempts to place all items using a greedy 3D packing algorithm.
6. Returns the first box that successfully fits all items.

If no suitable box is found, the system returns an appropriate error message.

---

## Project Architecture

```
Order
   │
   ▼
update_recommendation()
   │
   ▼
solve_packing()
   │
   ▼
ShipmentRecommendation
```

The project is organized into the following layers:

- **Models** – Store products, boxes, orders, and recommendations
- **Services** – Handle recommendation generation
- **Packing Solver** – Contains the box selection algorithm
- **Views & APIs** – REST endpoints and dashboard
- **Admin** – Manage data through Django Admin

---

## Database Models

| Model | Description |
|-------|-------------|
| Product | Product dimensions and weight |
| Box | Available shipping boxes with dimensions, weight limit, and cost |
| Order | Customer order |
| OrderItem | Products belonging to an order |
| ShipmentRecommendation | Stores the generated recommendation |

---

## Tech Stack

- Python 3.11
- Django 5.2
- Django REST Framework
- SQLite
- Pytest
- Git & GitHub

---

## Installation

Clone the repository.

```bash
git clone <repository-url>

cd AI_Assisted_Box_Selection_System
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run database migrations.

```bash
python manage.py migrate
```

(Optional) Load demo data.

```bash
python manage.py seed_demo_data
```

Create an admin account.

```bash
python manage.py createsuperuser
```

Run the development server.

```bash
python manage.py runserver
```

---

## Application URLs

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:8000/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| REST API | http://127.0.0.1:8000/api/ |

---

## REST API

### Products

| Method | Endpoint |
|---------|----------|
| GET | `/api/products/` |
| POST | `/api/products/` |

### Boxes

| Method | Endpoint |
|---------|----------|
| GET | `/api/boxes/` |
| POST | `/api/boxes/` |

### Orders

| Method | Endpoint |
|---------|----------|
| GET | `/api/orders/` |
| POST | `/api/orders/` |

### Order Details

| Method | Endpoint |
|---------|----------|
| GET | `/api/orders/<id>/` |

### Generate Recommendation

| Method | Endpoint |
|---------|----------|
| POST | `/api/orders/<id>/recommend/` |

---

## Example Request

```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
-H "Content-Type: application/json" \
-d '{
    "order_number":"ORD-1001",
    "customer_name":"John Doe",
    "items":[
        {
            "product_id":1,
            "quantity":2
        }
    ]
}'
```

---

## Running Tests

Using Django:

```bash
python manage.py test
```

Using Pytest:

```bash
pytest
```

---

## Project Structure

```
AI_Assisted_Box_Selection_System/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── box_selection/
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo_data.py
│   ├── templates/
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_solver.py
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── packing_solver.py
│   ├── urls.py
│   └── views.py
│
├── box_selection_project/
│
├── .gitignore
├── AI_USAGE.md
├── CHAT_TRANSCRIPT.md
├── LEARNINGS.md
├── README.md
├── TEST_OUTPUT.md
├── manage.py
├── pytest.ini
├── requirements.txt
└── db.sqlite3
```

---

## Design Decisions

- Selected the cheapest valid box instead of the smallest by volume.
- Used a greedy packing algorithm to keep the solution simple and maintainable.
- Allowed item rotation while packing.
- Stored packing layouts as JSON for easy visualization and API responses.
- Kept recommendation generation in a separate service layer to improve code organization.

---

## Limitations

- Uses a greedy heuristic rather than an optimal packing algorithm.
- Supports only single-box shipments.
- Does not consider fragile items or stacking rules.
- Packing accuracy depends on the heuristic and may not find every valid arrangement.

---

## Future Improvements

- Support multi-box shipments.
- Improve packing heuristics.
- Add box visualization in 3D.
- Add authentication and user management.
- Deploy using PostgreSQL and Docker.

---

## Submission Files

- ✅ README.md
- ✅ AI_USAGE.md
- ✅ LEARNINGS.md
- ✅ Test cases
- ✅ TEST_OUTPUT.md
- ✅ GitHub Repository
- ✅ Chat Transcript

---

## License

This project was developed for educational and technical evaluation purposes.