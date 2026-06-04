# P0054I Next Package Recommendation

Create:

```text
P0054J LABB SE1 consumption price forecast ablation train-through-May-2025
```

P0054J should run the actual downstream experiment:

- no_price vs with_p0054h_price_forecast
- train_fit through May 2025
- holdout from June 2025 onward
- identical row sets per compared model
- no actual future spot price features
- no production/export/import/A61/future-flow features
- no API/device/runtime work
