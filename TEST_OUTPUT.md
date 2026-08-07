# Test Run Output

**Date:** 2026-08-07  
**Environment:** Windows 11, Python 3.13, Django 5.2.17, DRF 3.17.2  
**Command:** `python manage.py test -v 2`

```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, box_selection, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying box_selection.0001_initial... OK
  Applying box_selection.0002_shipmentrecommendation_error_reason... OK
  Applying box_selection.0003_alter_box_depth_alter_box_height_and_more... OK
  Applying sessions.0001_initial...

test_dashboard_get_renders_successfully (box_selection.tests.test_api.APITests.test_dashboard_get_renders_successfully)
Verify dashboard GET renders correctly with products, orders, and recommendation details. ... ok
test_dashboard_post_creates_orders (box_selection.tests.test_api.APITests.test_dashboard_post_creates_orders)
Verify dashboard POST creates orders successfully. ... ok
test_dashboard_post_rejects_duplicate_order_number (box_selection.tests.test_api.APITests.test_dashboard_post_rejects_duplicate_order_number)
Verify duplicate order numbers are rejected in dashboard. ... ok
test_dashboard_post_rejects_empty_items (box_selection.tests.test_api.APITests.test_dashboard_post_rejects_empty_items)
Verify orders without items are rejected in dashboard. ... ok
test_get_order_detail (box_selection.tests.test_api.APITests.test_get_order_detail)
Verify GET /api/orders/<id>/ returns order details. ... ok
test_get_order_detail_non_existent (box_selection.tests.test_api.APITests.test_get_order_detail_non_existent)
Verify GET /api/orders/<id>/ returns HTTP 404 for non-existent order. ... ok
test_get_orders_list (box_selection.tests.test_api.APITests.test_get_orders_list)
Verify GET /api/orders/ returns the expected response and structure. ... ok
test_post_create_order_invalid_payload (box_selection.tests.test_api.APITests.test_post_create_order_invalid_payload)
Verify invalid requests return HTTP 400. ... ok
test_post_create_order_with_recommendation (box_selection.tests.test_api.APITests.test_post_create_order_with_recommendation)
Verify POST /api/orders/ creates an order and computes a recommendation. ... ok
test_post_recalculate_recommendation (box_selection.tests.test_api.APITests.test_post_recalculate_recommendation)
Verify POST /api/orders/<id>/recommend/ recalculates recommendations. ... ok
test_post_recalculate_recommendation_non_existent (box_selection.tests.test_api.APITests.test_post_recalculate_recommendation_non_existent)
Verify POST /api/orders/<id>/recommend/ returns HTTP 404 for non-existent order. ... ok
test_box_string_representation (box_selection.tests.test_models.BoxModelTests.test_box_string_representation)
__str__ should include box details. ... ok
test_box_volume_calculation (box_selection.tests.test_models.BoxModelTests.test_box_volume_calculation)
Box volume should be width × height × depth. ... ok
test_negative_cost_validation (box_selection.tests.test_models.BoxModelTests.test_negative_cost_validation)
Cost cannot be negative. ... ok
test_negative_dimension_validation (box_selection.tests.test_models.BoxModelTests.test_negative_dimension_validation)
Negative dimensions should not be allowed. ... ok
test_valid_box_is_saved (box_selection.tests.test_models.BoxModelTests.test_valid_box_is_saved)
A valid box should be saved successfully. ... ok
test_zero_max_weight_validation (box_selection.tests.test_models.BoxModelTests.test_zero_max_weight_validation)
Maximum weight must be greater than zero. ... ok
test_negative_dimension_validation (box_selection.tests.test_models.ProductModelTests.test_negative_dimension_validation)
Negative dimensions should raise ValidationError. ... ok
test_product_string_representation (box_selection.tests.test_models.ProductModelTests.test_product_string_representation)
__str__ should return name and SKU. ... ok
test_product_volume_calculation (box_selection.tests.test_models.ProductModelTests.test_product_volume_calculation)
Product volume should be width × height × depth. ... ok
test_valid_product_is_saved (box_selection.tests.test_models.ProductModelTests.test_valid_product_is_saved)
A valid product should be saved successfully. ... ok
test_zero_dimension_validation (box_selection.tests.test_models.ProductModelTests.test_zero_dimension_validation)
Zero dimensions should raise ValidationError. ... ok
test_zero_weight_validation (box_selection.tests.test_models.ProductModelTests.test_zero_weight_validation)
Weight must be greater than zero. ... ok
test_data_persisted_correctly (box_selection.tests.test_services.ServiceTests.test_data_persisted_correctly)
Verify packing layout, utilization values, and error messages are persisted correctly. ... ok
test_existing_recommendation_updated (box_selection.tests.test_services.ServiceTests.test_existing_recommendation_updated)
Verify existing recommendations are updated. ... ok
test_order_status_changes_to_packed (box_selection.tests.test_services.ServiceTests.test_order_status_changes_to_packed)
Verify order status changes to Packed. ... ok
test_pending_status_retained_when_no_box_fits (box_selection.tests.test_services.ServiceTests.test_pending_status_retained_when_no_box_fits)
Verify Pending status is retained when no box fits. ... ok
test_recommendation_created_successfully (box_selection.tests.test_services.ServiceTests.test_recommendation_created_successfully)
Verify recommendations are created successfully. ... ok
test_does_overlap (box_selection.tests.test_solver.PackingSolverTests.test_does_overlap)
Test overlapping and non-overlapping placements in 3D space. ... ok
test_fits_by_dimensions (box_selection.tests.test_solver.PackingSolverTests.test_fits_by_dimensions)
Test product dimensions vs box dimensions matching (including rotation). ... ok
test_greedy_packing_no_overlap (box_selection.tests.test_solver.PackingSolverTests.test_greedy_packing_no_overlap)
Verify the greedy packing algorithm places items without overlap. ... ok
test_orientations (box_selection.tests.test_solver.PackingSolverTests.test_orientations)
Test that all unique dimension permutations of a product are correctly returned. ... ok
test_solve_packing_cheapest_valid_box (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_cheapest_valid_box)
Verify that the solver always selects the lowest-cost box capable of packing the order. ... ok
test_solve_packing_dimension_constraints (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_dimension_constraints)
Verify dimension constraints filter out boxes too small for individual items. ... ok
test_solve_packing_empty_order (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_empty_order)
Verify empty orders return the correct error. ... ok
test_solve_packing_inactive_boxes_ignored (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_inactive_boxes_ignored)
Verify inactive boxes are ignored by the solver. ... ok
test_solve_packing_layout_valid_coordinates (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_layout_valid_coordinates)
Verify packing layout contains valid coordinates for every packed item. ... ok
test_solve_packing_utilization_calculation (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_utilization_calculation)
Verify volume utilization and weight utilization are calculated correctly. ... ok
test_solve_packing_weight_constraints (box_selection.tests.test_solver.PackingSolverTests.test_solve_packing_weight_constraints)
Verify weight constraints filter out invalid boxes. ... ok

----------------------------------------------------------------------
Ran 39 tests in 0.195s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

## Test Coverage Summary

| Category | Tests | Description |
| --- | --- | --- |
| Model | 12 | Volume calculation, validation rules, representation, and model integrity constraint validation. |
| Solver | 11 | Overlap, rotation permutations, dimension matching, greedy packing, weight constraints, dimension constraints, inactive filters, empty error behavior, utilization calculations, and coordinates verification. |
| Service | 5 | Recommendation persistence, update idempotency, order Packed/Pending status, error logging, and layout structure persistence. |
| API / UI | 11 | DRF endpoints (List, Detail, Recommend), validations, HTTP 400/404 responses, and Dashboard UI GET/POST interactions. |

**Result: 39/39 passed**

## CI

GitHub Actions workflow is configured at `.github/workflows/tests.yml` and runs the same test suite on push/PR to `main` or `master`.
