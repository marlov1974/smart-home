# P0054Y2 cluster segment dictionary

Status: `ADDED_AFTER_OPERATOR_REVIEW`

P0054Y2 cluster ids encode:

```text
C<climate_index><urban_load_index>
```

Climate index:

```text
1 = EAST_COAST_MALARDALEN_STOCKHOLM
2 = WEST_COAST_GOTHENBURG
3 = NORTHERN_INLAND
4 = SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
```

Urban/load index:

```text
1 = BIG_CITY_APARTMENT_SERVICE
2 = VILLA_SUBURBAN
3 = MIXED_SMALL_CITY_TOWN
4 = RURAL_SPARSE_AGRICULTURE
```

All clusters are `profiled/load-profile` components only. They are not full SE3 load and not observed metered/non-profiled load.

## Segment definitions

| cluster_id | segment | intended meaning | current MGA count | current profiled MWh |
|---|---|---|---:|---:|
| C11 | East coast / Mälardalen / Stockholm x big-city apartment/service | Dense eastern metropolitan profiled load: apartment/service dominated load in Stockholm/Mälardalen-style areas, generally high base load and large volume. | 3 | 5,532,939.368 |
| C12 | East coast / Mälardalen / Stockholm x villa/suburban | Eastern suburban and commuter-belt profiled load: villas/small properties around Mälardalen/Stockholm coast with stronger seasonal heating shape. | 5 | 2,439,114.556 |
| C13 | East coast / Mälardalen / Stockholm x mixed small-city/town | Eastern mixed-town profiled load: smaller cities/towns with mixed residential/service behavior and moderate volume. | 1 | 117,887.073 |
| C14 | East coast / Mälardalen / Stockholm x rural/sparse/agriculture | Eastern rural/sparse profiled load: low-density countryside/agriculture-style load in the east/Mälardalen region. Empty in current heuristic assignment. | 0 | 0.000 |
| C21 | West coast / Gothenburg x big-city apartment/service | Gothenburg/west-coast metropolitan profiled load: dense urban apartment/service load around Gothenburg-type areas. | 2 | 2,447,452.997 |
| C22 | West coast / Gothenburg x villa/suburban | West-coast suburban profiled load: villa/commuter-belt and coastal-town areas around Gothenburg/west-coast geography. | 10 | 2,667,301.708 |
| C23 | West coast / Gothenburg x mixed small-city/town | West-coast mixed-town profiled load: medium towns and mixed service/residential west-coast areas. Empty in current heuristic assignment. | 0 | 0.000 |
| C24 | West coast / Gothenburg x rural/sparse/agriculture | West-coast rural/sparse profiled load: low-density/agricultural or sparse west-coast hinterland areas. Empty in current heuristic assignment. | 0 | 0.000 |
| C31 | Northern inland x big-city apartment/service | Northern/inland high-volume profiled load: larger inland regional load pools treated as big-city/service-like by volume/base-load heuristics. | 1 | 1,827,535.485 |
| C32 | Northern inland x villa/suburban | Northern/inland villa/suburban profiled load: colder inland residential areas with clear heating-season signal. | 8 | 2,239,870.970 |
| C33 | Northern inland x mixed small-city/town | Northern/inland mixed-town profiled load: inland towns with mixed residential/service behavior. | 1 | 478,484.905 |
| C34 | Northern inland x rural/sparse/agriculture | Northern/inland sparse profiled load: rural/small-load inland areas with low density. Empty in current heuristic assignment. | 0 | 0.000 |
| C41 | Southern inland / Småland / north Götaland x big-city apartment/service | Southern-inland high-density profiled load: large dense/service-like southern inland areas. Empty in current heuristic assignment. | 0 | 0.000 |
| C42 | Southern inland / Småland / north Götaland x villa/suburban | Southern-inland villa/suburban profiled load: broad default residential/suburban group for many SE3 distribution MGAs outside named east/west/north regions. | 119 | 27,311,441.401 |
| C43 | Southern inland / Småland / north Götaland x mixed small-city/town | Southern-inland mixed-town profiled load: medium towns and regional centers with mixed residential/service profiles. | 14 | 7,982,322.327 |
| C44 | Southern inland / Småland / north Götaland x rural/sparse/agriculture | Southern-inland rural/sparse profiled load: small or sparse countryside/agriculture-style profiled load. | 6 | 282,498.981 |

## Empty-cluster interpretation

Clusters with `0` current MGAs are retained intentionally so the decomposition has a stable 4 x 4 contract. A zero-volume cluster means the current deterministic heuristic did not assign any loaded P0054W MGA to that segment. It does not prove the physical segment is absent in SE3.

## Quality note

The current assignment is LABB-grade and deterministic. It uses local names, owners and load-shape heuristics without external GIS, municipality, housing or industry enrichment. Future packages may improve assignments, but must preserve the distinction between:

```text
profiled/load-profile clusters
metered/non_profiled residual
full SE3 total
```
