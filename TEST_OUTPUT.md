# Test Run Output

**Date:** 2026-08-06  
**Environment:** Windows 10, Python 3.13, Django 5.2.17, DRF 3.17.2  
**Command:** `python manage.py test box_selection -v 2`

```
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

Found 18 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, box_selection, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
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
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).

test_create_order_via_api (box_selection.tests.APITests.test_create_order_via_api) ... ok
test_get_order_details_api (box_selection.tests.APITests.test_get_order_details_api) ... ok
test_recommend_endpoint_api (box_selection.tests.APITests.test_recommend_endpoint_api) ... ok
test_rejects_zero_quantity_items (box_selection.tests.APITests.test_rejects_zero_quantity_items) ... ok
test_box_validation (box_selection.tests.ModelTests.test_box_validation) ... ok
test_box_volume_calculation (box_selection.tests.ModelTests.test_box_volume_calculation) ... ok
test_invalid_product_save_is_rejected (box_selection.tests.ModelTests.test_invalid_product_save_is_rejected) ... ok
test_product_validation (box_selection.tests.ModelTests.test_product_validation) ... ok
test_product_volume_calculation (box_selection.tests.ModelTests.test_product_volume_calculation) ... ok
test_cheapest_box_selection (box_selection.tests.SolverTests.test_cheapest_box_selection) ... ok
test_empty_order_returns_error (box_selection.tests.SolverTests.test_empty_order_returns_error) ... ok
test_inactive_boxes_are_skipped (box_selection.tests.SolverTests.test_inactive_boxes_are_skipped) ... ok
test_non_overlapping_placements (box_selection.tests.SolverTests.test_non_overlapping_placements) ... ok
test_rejects_all_boxes_when_single_item_exceeds_all (box_selection.tests.SolverTests.test_rejects_all_boxes_when_single_item_exceeds_all) ... ok
test_rejects_all_boxes_when_weight_exceeds_all (box_selection.tests.SolverTests.test_rejects_all_boxes_when_weight_exceeds_all) ... ok
test_rotation_handling (box_selection.tests.SolverTests.test_rotation_handling) ... ok
test_selects_larger_box_when_dimensions_exceed (box_selection.tests.SolverTests.test_selects_larger_box_when_dimensions_exceed) ... ok
test_selects_larger_box_when_weight_exceeds (box_selection.tests.SolverTests.test_selects_larger_box_when_weight_exceeds) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.137s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

## Test Coverage Summary

| Category | Tests | Description                                                                                                           |
| -------- | ----- | --------------------------------------------------------------------------------------------------------------------- |
| Model    | 5     | Volume calculation, validation rules, and save-time validation                                                        |
| Solver   | 9     | Cheapest box selection, dimension/weight limits, rotation, overlap checks, empty order, inactive boxes, failure cases |
| API      | 4     | Order creation, order detail, recommendation endpoint, and invalid quantity handling                                  |

**Result: 18/18 passed**

## CI

GitHub Actions workflow is configured at `.github/workflows/tests.yml` and runs the same test suite on push/PR to `main` or `master`.
