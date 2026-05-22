# Router / NAT Rules

## Operator-side access

External/operator-side reachable base address when at home:

```text
192.168.86.240
```

Port-forwarding convention:

```text
external port = 80xx
xx = last octet of the internal Shelly IP address
```

Example:

```text
Internal: 192.168.77.40
NAT URL:  http://192.168.86.240:8040/
```

Example KVS read through NAT:

```text
http://192.168.86.240:8040/rpc/KVS.Get?key=ftx.weather.act
```

Internal equivalent, only valid inside the technical network:

```text
http://192.168.77.40/rpc/KVS.Get?key=ftx.weather.act
```

## Rule

Use NAT URLs for manual/operator troubleshooting unless the user explicitly asks for internal URLs.

Use internal `192.168.77.x` URLs for Shelly runtime device-to-device code.

## Source

Imported from G1 `marlov1974/shelly` device-topology memory during `P0002`.
