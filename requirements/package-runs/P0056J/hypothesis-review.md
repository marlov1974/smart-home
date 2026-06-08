# P0056J Hypothesis Review

| conclusion | hypothesis |
| --- | --- |
| supported | H1 static and rolling evaluate different target rows / horizon mix |
| supported | H2 static and rolling use different lag-feature construction |
| supported | H3 static and rolling use different weather-feature construction |
| supported | H4 static and rolling use different horizon-bias correction |
| supported | H5 static and rolling use different train/validation windows |
| supported | H6 static metric is row-wise holdout prediction, not origin-realistic forecast |
| rejected | H7 rolling pipeline has a target/horizon alignment bug |
| inconclusive | H8 rolling feature column order or missing handling differs |
| supported | gap remains on reconstructed target-aligned intersection |
