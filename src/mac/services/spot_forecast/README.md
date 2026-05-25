# Spot Forecast Service

P0017 Mac service for compact weekly spot period indexes.

Run one deterministic forecast:

```bash
python3 -m src.mac.services.spot_forecast --once --week 2
```

Run the local trusted HTTP service:

```bash
python3 -m src.mac.services.spot_forecast --host 127.0.0.1 --port 8080
```

Endpoint:

```text
GET /spot/period-index?week=WW
```

Success response is a compact JSON array with 21 two-decimal numbers.

