# P0054W native-resolution contract

P0054W stores native source timestamps directly in `esett_mga_consumption_native_v1`.

`resolution_minutes` is inferred from adjacent source timestamps per response. Values are not resampled to hourly and source negative consumption sign is preserved.
