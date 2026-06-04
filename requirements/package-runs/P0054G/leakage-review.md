# P0054G Leakage Review

## Existing P0053C-B Validation/Holdout Rows

P0053C-B evidence reports:

| check | result |
|---|---|
| `anchor_price_timestamps_strictly_before_origin` | pass |
| `no_target_window_actual_price_used_for_anchor` | pass |
| `input_cutoff_not_after_origin` | pass |
| `forecast_origin_not_after_target` | pass |
| `holdout_used_for_selection` | false |
| `a61_used` | false |
| `api_or_device_used` | false |

P0054G accepts that existing validation/holdout source as forecast-origin-safe for its documented rows.

## Proposed Train Extension Using Existing Global M4

Result: FAIL CLOSED.

Reason:

The upstream P0045/P0053C-B shape model is trained on the full canonical train split. For forecast origins inside the train split, that model has seen target rows later than the origin/cutoff. That violates the forecast-origin feature rule.

This is not target-window anchor leakage; it is upstream model-training leakage relative to train-period origins.

## Live/Forbidden Inputs

P0054G did not use:

- live market API
- Shelly/Home Assistant/device/runtime writes
- A61 capacity/utilization
- future production/export/import/flow features
- target-window actual spot price as a forecast feature
- holdout for fitting or selection

## Conclusion

No train-period forecast log was generated because the current safe reuse path would fail leakage review.
