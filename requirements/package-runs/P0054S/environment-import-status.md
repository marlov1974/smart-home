# P0054S LABB

Status: `PASS`

```json
{
  "imports": {
    "lightgbm": {
      "ok": true,
      "version": "4.6.0"
    },
    "xgboost": {
      "ok": true,
      "version": "2.1.4"
    }
  },
  "optional_sequence_imports": {
    "tensorflow": {
      "error": "No module named 'tensorflow'",
      "error_type": "ModuleNotFoundError",
      "ok": false
    },
    "torch": {
      "error": "No module named 'torch'",
      "error_type": "ModuleNotFoundError",
      "ok": false
    }
  },
  "packages": {
    "lightgbm": "4.6.0",
    "numpy": "2.0.2",
    "scikit-learn": "1.6.1",
    "xgboost": "2.1.4"
  }
}
```
