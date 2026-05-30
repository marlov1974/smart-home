# P0029 attempts

## Attempt 1

Status: passed after sandbox-aware rerun.

Implementation:

- Added `src/mac/services/chatgpt_mcp_access/`.
- Added local Streamable HTTP MCP endpoint at `POST /mcp`.
- Bound to localhost only by default.
- Reused P0028 `handle_mcp_message(...)`.
- Added unit tests under `tests/mac/services/chatgpt_mcp_access/`.
- Added durable function docs.

Initial test issue:

```text
python3 -m unittest discover tests/mac/services/chatgpt_mcp_access
=> PermissionError: [Errno 1] Operation not permitted
```

Cause:

```text
Sandbox blocked localhost socket bind for HTTP server tests.
```

Resolution:

```text
Reran with approved escalation for python3 -m unittest.
Added tests/mac/services/chatgpt_mcp_access/__init__.py so tests/mac/services discovery includes P0029 tests.
Added Content-Length: 0 to empty HTTP responses after one test observed a connection reset when reading a 403 response body.
```

Final unit test results:

```text
python3 -m unittest discover tests/mac/services/chatgpt_mcp_access
=> Ran 10 tests OK

python3 -m unittest discover tests/mac/services/local_operator_mcp
=> Ran 10 tests OK

python3 -m unittest discover tests/mac/services/local_operator_bridge
=> Ran 9 tests OK

python3 -m unittest discover tests/mac/tools/local_kvs_read
=> Ran 10 tests OK

python3 -m unittest discover tests/mac/services
=> Ran 29 tests OK

python3 -m unittest discover tests/mac/tools
=> Ran 68 tests OK
```

Local smoke test:

```text
server:
python3 -m src.mac.services.chatgpt_mcp_access serve --host 127.0.0.1 --port 8765

tools/list:
HTTP 200
MCP-Protocol-Version: 2025-06-18
tools: shelly_kvs_get_by_nat_octet only

tools/call:
tool: shelly_kvs_get_by_nat_octet
octet: 30
key: hp.price.status
timeout: 5
HTTP 200
MCP isError: false
P0026 result_status: success
P0026 HTTP status: 200
value: "ok"
derived URL: http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status
```

The local smoke server was stopped after verification using:

```text
pkill -f src.mac.services.chatgpt_mcp_access
```

Safety:

```text
No KVS.Set, Script.*, actuator call, generic proxy, arbitrary URL fetch, shell execution, Codex runner, public exposure or persistent service installation was added or used.
```
