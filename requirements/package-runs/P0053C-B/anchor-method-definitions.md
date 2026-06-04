# P0053C-B anchor method definitions

```json
{
  "A0_mean_std": "level=mean(hist48), scale=population_std(hist48), pred=level+shape*scale",
  "A1_median_iqr": "level=median(hist48), scale=(q75-q25)/1.349, pred=level+shape*scale",
  "A2_last24_last48_blend_iqr": "level=0.5*mean(last24)+0.5*mean(hist48), scale=(q75-q25)/1.349, pred=level+shape*scale",
  "A3_same_hour_48h_iqr": "level=mean(previous 48h prices with same fixed-CET hour), scale=(q75-q25)/1.349, pred=level+shape*scale"
}
```
