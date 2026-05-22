# Network and Access Principles

## Technical network

Shelly devices communicate internally on the technical network using:

```text
192.168.77.x
```

Device-to-device code should use internal `192.168.77.x` addresses.

## Operator access

The operator is normally outside the technical network, even when physically at home.

Manual browser/RPC access should normally use the operator-side NAT endpoint unless explicitly working from inside the technical network.

Operator-side reachable base address at home:

```text
192.168.86.240
```

## Tailscale / Mac access

The Mac mini / developer host may later provide Tailscale, SSH, Codex and diagnostic access.

Tailscale is an operator/developer access layer. It does not replace internal Shelly device addressing used by runtime code.

## Rule

Runtime code between Shelly devices uses internal technical-network IPs.

User-facing troubleshooting URLs should normally use NAT URLs from `router-nat.md`.

## Source

Imported from G1 `marlov1974/shelly` device-topology memory during `P0002`.
