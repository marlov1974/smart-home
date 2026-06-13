import ast
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.mac.tools.shelly_live.core import (
    ALLOWED_SCRIPT_NAME,
    FTX_STATE_HIST_KVS_KEY,
    FTX_STATE_RUN_KVS_KEY,
    FTX_STATE_SCRIPT_NAME,
    HELLO_SCRIPT_NAME,
    SPOTPRICE_KVS_KEYS,
    SPOTPRICE_SCRIPT_NAME,
    SUPPLY_UNI_KVS_KEY,
    SUPPLY_UNI_PUB_SCRIPT_NAME,
    SUPPLY_UNI_REFRESH_SCRIPT_NAME,
    WEATHER_KVS_KEY,
    WEATHER_SCRIPT_NAME,
    ShellyLiveError,
    build_ftx_recipe_script,
    capture_debug_log,
    deploy_ftx_state,
    deploy_hello,
    deploy_spotprice,
    deploy_supply_uni,
    deploy_weather,
    ensure_allowed_script_name,
    ensure_script,
    find_script,
    normalize_base_url,
    parse_supply_status,
    put_script_code,
    put_script_code_chunked,
    rpc_call,
    split_rpc_upload_chunks,
    supply_snapshot_changed,
    verify_supply_snapshot,
    verify_spotprice_kvs,
    verify_weather_kvs,
)


class FakeResponse:
    def __init__(self, body=b"", lines=None):
        self.body = body
        self.lines = list(lines or [])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body

    def readline(self):
        if self.lines:
            return self.lines.pop(0)
        return b""


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, timeout=0):
        self.requests.append((request, timeout))
        if not self.responses:
            raise AssertionError("no fake response queued")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def rpc_response(result):
    return FakeResponse(json.dumps({"id": 1, "result": result}).encode("utf-8"))


class ShellyLiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.script_path = self.tmp / "hello_v1_0_0.js"
        self.script_path.write_text('print("hello world");\n', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_normalize_base_url_strips_trailing_slash(self):
        self.assertEqual("http://device", normalize_base_url("http://device/"))

    def test_rpc_call_posts_json_rpc_body(self):
        opener = FakeOpener([rpc_response({"ok": True})])

        result = rpc_call("http://device/", "Script.List", opener=opener)

        self.assertEqual({"ok": True}, result)
        request, timeout = opener.requests[0]
        self.assertEqual("http://device/rpc", request.full_url)
        self.assertEqual("POST", request.get_method())
        self.assertEqual(5.0, timeout)
        self.assertEqual({"id": 1, "method": "Script.List"}, json.loads(request.data.decode("utf-8")))

    def test_rpc_call_raises_for_rpc_error(self):
        opener = FakeOpener([FakeResponse(b'{"id":1,"error":{"code":-1,"message":"bad"}}')])

        with self.assertRaisesRegex(ShellyLiveError, "returned error"):
            rpc_call("http://device", "Script.List", opener=opener)

    def test_find_script_matches_exact_name(self):
        scripts = [{"id": 1, "name": "other"}, {"id": 2, "name": ALLOWED_SCRIPT_NAME}]

        self.assertEqual({"id": 2, "name": ALLOWED_SCRIPT_NAME}, find_script(scripts, ALLOWED_SCRIPT_NAME))
        self.assertIsNone(find_script(scripts, "missing"))

    def test_forbidden_script_name_is_rejected(self):
        ensure_allowed_script_name(ALLOWED_SCRIPT_NAME)
        ensure_allowed_script_name(SPOTPRICE_SCRIPT_NAME)
        ensure_allowed_script_name(WEATHER_SCRIPT_NAME)
        ensure_allowed_script_name(SUPPLY_UNI_PUB_SCRIPT_NAME)
        ensure_allowed_script_name(SUPPLY_UNI_REFRESH_SCRIPT_NAME)
        ensure_allowed_script_name(FTX_STATE_SCRIPT_NAME)

        with self.assertRaisesRegex(ShellyLiveError, "forbidden script name"):
            ensure_allowed_script_name("g2-hello")

    def test_ensure_script_reuses_existing_allowed_script(self):
        opener = FakeOpener([rpc_response({"scripts": [{"id": 7, "name": ALLOWED_SCRIPT_NAME}]})])

        self.assertEqual(7, ensure_script("http://device", opener=opener))
        self.assertEqual(1, len(opener.requests))

    def test_ensure_script_creates_missing_allowed_script(self):
        opener = FakeOpener([rpc_response({"scripts": []}), rpc_response({"id": 8})])

        self.assertEqual(8, ensure_script("http://device", opener=opener))
        body = json.loads(opener.requests[1][0].data.decode("utf-8"))
        self.assertEqual("Script.Create", body["method"])
        self.assertEqual({"name": ALLOWED_SCRIPT_NAME}, body["params"])

    def test_put_script_code_uses_only_script_rpc(self):
        opener = FakeOpener([rpc_response({})])

        put_script_code("http://device", 9, ALLOWED_SCRIPT_NAME, "print(1);", opener=opener)

        body = json.loads(opener.requests[0][0].data.decode("utf-8"))
        self.assertEqual("Script.PutCode", body["method"])
        self.assertEqual({"id": 9, "code": "print(1);", "append": False}, body["params"])

    def test_split_rpc_upload_chunks_uses_multiple_bounded_chunks(self):
        chunks = split_rpc_upload_chunks("abcdef", upload_chunk_bytes=2)

        self.assertEqual(["ab", "cd", "ef"], chunks)

        with self.assertRaisesRegex(ShellyLiveError, "positive"):
            split_rpc_upload_chunks("abc", upload_chunk_bytes=0)

    def test_put_script_code_chunked_appends_after_first_chunk(self):
        opener = FakeOpener([rpc_response({}), rpc_response({}), rpc_response({})])

        count = put_script_code_chunked(
            "http://device",
            10,
            SPOTPRICE_SCRIPT_NAME,
            "abcdef",
            upload_chunk_bytes=2,
            opener=opener,
        )

        self.assertEqual(3, count)
        params = [
            json.loads(request.data.decode("utf-8"))["params"]
            for request, _timeout in opener.requests
        ]
        self.assertEqual(
            [
                {"id": 10, "code": "ab", "append": False},
                {"id": 10, "code": "cd", "append": True},
                {"id": 10, "code": "ef", "append": True},
            ],
            params,
        )

    def test_build_ftx_recipe_script_maps_rt_chunks_to_ftx_root(self):
        ftx_root = self.tmp / "ftx"
        (ftx_root / "recipes").mkdir(parents=True)
        (ftx_root / "common").mkdir()
        (ftx_root / "state").mkdir()
        (ftx_root / "common" / "wrapper.start.js").write_text("(function () {\n", encoding="utf-8")
        (ftx_root / "state" / "main.js").write_text("print('state DON');\n", encoding="utf-8")
        (ftx_root / "recipes" / "state.json").write_text(
            json.dumps({"chunks": ["rt/common/wrapper.start.js", "rt/state/main.js"]}),
            encoding="utf-8",
        )

        built = build_ftx_recipe_script(ftx_root / "recipes" / "state.json")

        self.assertEqual("(function () {\nprint('state DON');\n", built)

    def test_verify_spotprice_kvs_accepts_valid_price_series(self):
        values = {
            "hp.price.2h": "1,2,3,4,5,6,7,8,9,10,11,12",
            "hp.price.date": "2026-05-24",
            "hp.price.area": "SE3",
            "hp.price.status": "ok",
            "hp.price.updated": "2026-05-24T12:00:00",
        }

        summary = verify_spotprice_kvs(values)

        self.assertEqual("ok", summary["status"])
        self.assertEqual("SE3", summary["area"])
        self.assertEqual(12, summary["price_count"])
        self.assertEqual(1.0, summary["price_min"])
        self.assertEqual(12.0, summary["price_max"])

    def test_verify_spotprice_kvs_rejects_non_ok_status(self):
        values = {
            "hp.price.2h": "1,2,3,4,5,6,7,8,9,10,11,12",
            "hp.price.date": "2026-05-24",
            "hp.price.area": "SE3",
            "hp.price.status": "fetching",
            "hp.price.updated": "2026-05-24T12:00:00",
        }

        with self.assertRaisesRegex(ShellyLiveError, "status is not ok"):
            verify_spotprice_kvs(values)

    def test_verify_spotprice_kvs_rejects_wrong_area(self):
        values = {
            "hp.price.2h": "1,2,3,4,5,6,7,8,9,10,11,12",
            "hp.price.date": "2026-05-24",
            "hp.price.area": "SE4",
            "hp.price.status": "ok",
            "hp.price.updated": "2026-05-24T12:00:00",
        }

        with self.assertRaisesRegex(ShellyLiveError, "area is not SE3"):
            verify_spotprice_kvs(values)

    def test_verify_spotprice_kvs_rejects_malformed_price_series(self):
        with self.assertRaisesRegex(ShellyLiveError, "12 values"):
            verify_spotprice_kvs({"hp.price.status": "ok", "hp.price.area": "SE3", "hp.price.2h": "1,2"})

    def test_spotprice_kvs_get_missing_key_returns_none(self):
        from src.mac.tools.shelly_live.core import kvs_get

        opener = FakeOpener(
            [FakeResponse(b'{"id":1,"error":{"code":-105,"message":"Argument key not found!"}}')]
        )

        self.assertIsNone(kvs_get("http://device", "hp.price.2h", opener=opener))

    def test_capture_debug_log_stops_when_expected_text_appears(self):
        opener = FakeOpener([FakeResponse(lines=[b"boot\n", b"hello world\n"])])

        excerpt = capture_debug_log("http://device", "hello", opener=opener)

        self.assertIn("hello world", excerpt)
        self.assertEqual("http://device/debug/log", opener.requests[0][0].full_url)

    def test_deploy_hello_orchestrates_allowed_rpc_sequence(self):
        opener = FakeOpener(
            [
                rpc_response({"online": True}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 3}),
                rpc_response({}),
                FakeResponse(lines=[b"hello world\n"]),
                rpc_response({}),
                rpc_response({}),
                rpc_response({"scripts": [{"id": 3, "name": ALLOWED_SCRIPT_NAME, "running": False}]}),
            ]
        )

        result = deploy_hello("http://device", self.script_path, opener=opener)

        self.assertEqual(ALLOWED_SCRIPT_NAME, result.script_name)
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetStatus",
                "Script.List",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.Start",
                "Script.Stop",
                "Script.List",
            ],
            methods,
        )
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "KVS.", "Wifi.", "Mqtt.", "Bluetooth.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_deploy_spotprice_cleans_hello_uploads_chunks_and_reads_kvs(self):
        self.script_path.write_text("abcdefghij", encoding="utf-8")
        kvs_responses = []
        kvs_values = {
            "hp.price.2h": "1,2,3,4,5,6,7,8,9,10,11,12",
            "hp.price.date": "2026-05-24",
            "hp.price.area": "SE3",
            "hp.price.status": "ok",
            "hp.price.updated": "2026-05-24T12:00:00",
        }
        for key in SPOTPRICE_KVS_KEYS:
            kvs_responses.append(rpc_response({"value": kvs_values[key]}))
        opener = FakeOpener(
            [
                rpc_response({"online": True}),
                rpc_response({"scripts": [{"id": 3, "name": HELLO_SCRIPT_NAME, "running": True}]}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 10}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({}),
                FakeResponse(lines=[b"spotprice NO TOKEN\n"]),
                rpc_response({}),
                *kvs_responses,
                rpc_response({}),
                rpc_response({"scripts": [{"id": 10, "name": SPOTPRICE_SCRIPT_NAME, "running": False}]}),
            ]
        )

        result = deploy_spotprice(
            "http://device",
            self.script_path,
            upload_chunk_bytes=3,
            opener=opener,
        )

        self.assertTrue(result.cleaned_hello)
        self.assertEqual(4, result.upload_chunk_count)
        self.assertEqual(SPOTPRICE_SCRIPT_NAME, result.script_name)
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetStatus",
                "Script.List",
                "Script.Stop",
                "Script.Delete",
                "Script.List",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.PutCode",
                "Script.PutCode",
                "Script.PutCode",
                "Script.Start",
                "KVS.Get",
                "KVS.Get",
                "KVS.Get",
                "KVS.Get",
                "KVS.Get",
                "Script.Stop",
                "Script.List",
            ],
            methods,
        )
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "Wifi.", "Mqtt.", "Bluetooth.", "Virtual.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_spotprice_source_uses_p0013_low_memory_contract(self):
        source_path = Path(__file__).resolve().parents[4] / "src" / "shelly" / "spotprice" / "spotprice.js"
        source = source_path.read_text(encoding="utf-8")

        self.assertIn("se.elpris.eu/api/v1/prices", source)
        self.assertIn("?avg24", source)
        self.assertIn("hp.price.area", source)
        self.assertIn('var key = \'"p":[\';', source)
        self.assertNotIn("JSON.parse", source)
        self.assertNotIn("api.tibber.com", source)
        self.assertNotIn("hp.price.source", source)
        self.assertNotIn("hp.price.debug", source)
        self.assertNotIn("SEK_per_kWh", source)

    def test_verify_weather_kvs_accepts_valid_contract(self):
        summary = verify_weather_kvs(
            {
                "solar_kwh_today": 52,
                "temp_now": 21.94,
                "temp_avg_today": 18.44,
                "humidity_avg_today": 62,
            }
        )

        self.assertEqual(
            {
                "solar_kwh_today": 52,
                "temp_now": 21.9,
                "temp_avg_today": 18.4,
                "humidity_avg_today": 62.0,
            },
            summary,
        )

    def test_verify_weather_kvs_rejects_missing_contract(self):
        with self.assertRaisesRegex(ShellyLiveError, "not numeric"):
            verify_weather_kvs({"solar_kwh_today": 1})

    def test_deploy_weather_verifies_identity_uploads_chunks_and_reads_weather_kvs(self):
        self.script_path.write_text("abcdefghij", encoding="utf-8")
        weather_value = {
            "solar_kwh_today": 52,
            "temp_now": 21.9,
            "temp_avg_today": 18.4,
            "humidity_avg_today": 62,
        }
        opener = FakeOpener(
            [
                rpc_response({"id": "shellypro1pm-8813bfd99f54", "model": "SPSW-201PE15UL"}),
                rpc_response({"online": True}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 11}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({}),
                FakeResponse(lines=[b"weather_v0_9_0 BOT\n", b"weather_v0_9_0 DONE\n"]),
                rpc_response({}),
                rpc_response({"value": weather_value}),
                rpc_response({}),
                rpc_response({"scripts": [{"id": 11, "name": WEATHER_SCRIPT_NAME, "running": False}]}),
            ]
        )

        result = deploy_weather(
            "http://device",
            self.script_path,
            upload_chunk_bytes=3,
            opener=opener,
        )

        self.assertEqual(WEATHER_SCRIPT_NAME, result.script_name)
        self.assertEqual("shellypro1pm-8813bfd99f54", result.live_device_id)
        self.assertEqual(4, result.upload_chunk_count)
        self.assertEqual(52, result.kvs_summary["solar_kwh_today"])
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetDeviceInfo",
                "Shelly.GetStatus",
                "Script.List",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.PutCode",
                "Script.PutCode",
                "Script.PutCode",
                "Script.Start",
                "KVS.Get",
                "Script.Stop",
                "Script.List",
            ],
            methods,
        )
        kvs_requests = [
            request for request, _timeout in opener.requests
            if request.get_method() == "POST" and json.loads(request.data.decode("utf-8"))["method"] == "KVS.Get"
        ]
        self.assertEqual({"key": WEATHER_KVS_KEY}, json.loads(kvs_requests[0].data.decode("utf-8"))["params"])
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "Wifi.", "Mqtt.", "Bluetooth.", "Virtual.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_deploy_weather_rejects_wrong_identity(self):
        opener = FakeOpener([rpc_response({"id": "shellypro1pm-deadbeef0000"})])

        with self.assertRaisesRegex(ShellyLiveError, "identity mismatch"):
            deploy_weather("http://device", self.script_path, opener=opener)

    def test_deploy_weather_rejects_memory_pressure_log(self):
        self.script_path.write_text("abc", encoding="utf-8")
        opener = FakeOpener(
            [
                rpc_response({"id": "shellypro1pm-8813bfd99f54"}),
                rpc_response({"online": True}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 11}),
                rpc_response({}),
                FakeResponse(lines=[b"weather_v0_9_0 out_of_memory\n", b"weather_v0_9_0 DONE\n"]),
                rpc_response({}),
                rpc_response({}),
            ]
        )

        with self.assertRaisesRegex(ShellyLiveError, "memory pressure"):
            deploy_weather("http://device", self.script_path, upload_chunk_bytes=10, opener=opener)

    def test_weather_source_uses_p0015_g2_contract(self):
        source_path = Path(__file__).resolve().parents[4] / "src" / "shelly" / "weather" / "weather.js"
        source = source_path.read_text(encoding="utf-8")

        self.assertIn("weather_v0_9_0", source)
        self.assertIn("g2.weather.act", source)
        self.assertIn("relative_humidity_2m_mean", source)
        self.assertIn("humidity_avg_today", source)
        self.assertIn("api.open-meteo.com/v1/forecast", source)
        self.assertIn("Script.Stop", source)
        self.assertNotIn("ftx.weather.act", source)
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "MQTT.", "Wifi.", "Bluetooth.")
        self.assertFalse(any(fragment in source for fragment in forbidden_fragments))

    def test_deploy_ftx_state_uploads_runs_and_verifies_zero_vvx(self):
        ftx_root = self.tmp / "ftx"
        (ftx_root / "recipes").mkdir(parents=True)
        (ftx_root / "common").mkdir()
        (ftx_root / "state").mkdir()
        (ftx_root / "common" / "wrapper.start.js").write_text("(function () {\n", encoding="utf-8")
        (ftx_root / "state" / "main.js").write_text(
            "if (!ctx.run || !ctx.run.vvx) { print('guard'); }\nprint('state DON');\n",
            encoding="utf-8",
        )
        recipe_path = ftx_root / "recipes" / "state.json"
        recipe_path.write_text(
            json.dumps({"chunks": ["rt/common/wrapper.start.js", "rt/state/main.js"]}),
            encoding="utf-8",
        )
        opener = FakeOpener(
            [
                rpc_response({"id": "shellypro1pm-8813bfd99f54", "model": "SPSW-201PE15UL"}),
                rpc_response({"online": True}),
                rpc_response({"scripts": [{"id": 5, "name": FTX_STATE_SCRIPT_NAME, "running": False}]}),
                rpc_response({"scripts": [{"id": 5, "name": FTX_STATE_SCRIPT_NAME, "running": False}]}),
                rpc_response({}),
                FakeResponse(lines=[b"state BOT\n", b"state DON\n"]),
                rpc_response({}),
                rpc_response({"value": {"vvx": 0}}),
                rpc_response({"value": 0}),
                rpc_response({"value": {"r0": 0, "r1": 0, "r2": 0}}),
                rpc_response({"scripts": [{"id": 5, "name": FTX_STATE_SCRIPT_NAME, "running": False}]}),
            ]
        )

        result = deploy_ftx_state(
            "http://device",
            recipe_path,
            upload_chunk_bytes=1000,
            opener=opener,
        )

        self.assertEqual(FTX_STATE_SCRIPT_NAME, result.script_name)
        self.assertEqual("shellypro1pm-8813bfd99f54", result.live_device_id)
        self.assertEqual(1, result.upload_chunk_count)
        self.assertEqual(
            {"run_vvx": 0, "number_202": 0.0, "hist": {"r0": 0.0, "r1": 0.0, "r2": 0.0}},
            result.zero_vvx_summary,
        )
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetDeviceInfo",
                "Shelly.GetStatus",
                "Script.List",
                "Script.List",
                "Script.PutCode",
                "Script.Start",
                "KVS.Get",
                "Number.GetStatus",
                "KVS.Get",
                "Script.List",
            ],
            methods,
        )
        kvs_params = [
            json.loads(request.data.decode("utf-8"))["params"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST" and json.loads(request.data.decode("utf-8"))["method"] == "KVS.Get"
        ]
        self.assertEqual([{"key": FTX_STATE_RUN_KVS_KEY}, {"key": FTX_STATE_HIST_KVS_KEY}], kvs_params)
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "Wifi.", "Mqtt.", "Bluetooth.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_parse_supply_status_accepts_expected_component_keys(self):
        status = {
            "voltmeter:100": {"xvoltage": 42.2},
            "input:2": {"xfreq": 1234.4},
            "temperature:100": {"tC": 18.44},
            "temperature:101": {"tC": -3.24},
            "temperature:102": {"tC": 7.25},
        }

        self.assertEqual(
            {
                "supply_pa": 42,
                "outdoor": -3.2,
                "post_vvx": 18.4,
                "to_outdoor": 7.2,
                "supply_rpm": 1234,
            },
            parse_supply_status(status),
        )

    def test_parse_supply_status_rejects_missing_values(self):
        with self.assertRaisesRegex(ShellyLiveError, "missing required"):
            parse_supply_status({"voltmeter:100": {"xvoltage": 42}})

    def test_verify_supply_snapshot_accepts_exact_contract(self):
        summary = verify_supply_snapshot(
            {
                "t": 1780000000,
                "supply_pa": 42,
                "outdoor": -3.24,
                "post_vvx": 18.44,
                "to_outdoor": 7.25,
                "supply_rpm": 1234,
            }
        )

        self.assertEqual(
            {
                "t": 1780000000,
                "supply_pa": 42,
                "outdoor": -3.2,
                "post_vvx": 18.4,
                "to_outdoor": 7.2,
                "supply_rpm": 1234,
            },
            summary,
        )

    def test_verify_supply_snapshot_rejects_extra_keys(self):
        with self.assertRaisesRegex(ShellyLiveError, "keys mismatch"):
            verify_supply_snapshot(
                {
                    "t": 1780000000,
                    "source": "ftx-supply-uni",
                    "supply_pa": 42,
                    "outdoor": -3.2,
                    "post_vvx": 18.4,
                    "to_outdoor": 7.2,
                    "supply_rpm": 1234,
                }
            )

    def test_supply_snapshot_changed_uses_p0016_thresholds(self):
        previous = {
            "t": 1780000000,
            "supply_pa": 42,
            "outdoor": 1.0,
            "post_vvx": 18.0,
            "to_outdoor": 7.0,
            "supply_rpm": 1200,
        }
        below = {
            "t": 1780000015,
            "supply_pa": 51,
            "outdoor": 1.9,
            "post_vvx": 18.9,
            "to_outdoor": 7.9,
            "supply_rpm": 1299,
        }
        crossing = dict(below)
        crossing["supply_pa"] = 52

        self.assertTrue(supply_snapshot_changed(previous, None))
        self.assertFalse(supply_snapshot_changed(below, previous))
        self.assertTrue(supply_snapshot_changed(crossing, previous))

    def test_deploy_supply_uni_verifies_status_uploads_scripts_and_reads_kvs(self):
        publisher_path = self.tmp / "supply_uni_pub.js"
        refresher_path = self.tmp / "supply_uni_refresh.js"
        publisher_path.write_text("abcdef", encoding="utf-8")
        refresher_path.write_text("wxyz", encoding="utf-8")
        status = {
            "voltmeter:100": {"xvoltage": 42.2},
            "input:2": {"xfreq": 1234.4},
            "temperature:100": {"tC": 18.44},
            "temperature:101": {"tC": -3.24},
            "temperature:102": {"tC": 7.25},
        }
        kvs_value = {
            "t": 1780000000,
            "supply_pa": 42,
            "outdoor": -3.2,
            "post_vvx": 18.4,
            "to_outdoor": 7.2,
            "supply_rpm": 1234,
        }
        opener = FakeOpener(
            [
                rpc_response({"id": "shellyplusuni-aabbccddeeff", "model": "SNSN-0043X"}),
                rpc_response(status),
                rpc_response({"id": "shellypro1pm-8813bfd99f54", "model": "SPSW-201PE15UL"}),
                rpc_response({"online": True}),
                rpc_response({"scripts": []}),
                rpc_response({"scripts": []}),
                rpc_response({"id": 20}),
                rpc_response({}),
                rpc_response({}),
                rpc_response({"scripts": [{"id": 20, "name": SUPPLY_UNI_PUB_SCRIPT_NAME, "running": False}]}),
                rpc_response({"id": 21}),
                rpc_response({}),
                rpc_response({}),
                FakeResponse(lines=[b"supply_uni_pub BOT\n", b"supply_uni_pub PUB OK pa=42 rpm=1234\n"]),
                rpc_response({}),
                rpc_response({"value": kvs_value}),
                FakeResponse(lines=[b"supply_uni_refresh BOT\n", b"supply_uni_refresh DONE\n"]),
                rpc_response({}),
                rpc_response(
                    {
                        "scripts": [
                            {"id": 20, "name": SUPPLY_UNI_PUB_SCRIPT_NAME, "running": True},
                            {"id": 21, "name": SUPPLY_UNI_REFRESH_SCRIPT_NAME, "running": False},
                        ]
                    }
                ),
            ]
        )

        result = deploy_supply_uni(
            "http://supply",
            "http://dampers",
            publisher_path,
            refresher_path,
            upload_chunk_bytes=3,
            opener=opener,
        )

        self.assertEqual("shellyplusuni-aabbccddeeff", result.supply_device_id)
        self.assertEqual("shellypro1pm-8813bfd99f54", result.dampers_device_id)
        self.assertEqual(2, result.publisher_upload_chunk_count)
        self.assertEqual(2, result.refresher_upload_chunk_count)
        self.assertEqual(42, result.kvs_summary["supply_pa"])
        methods = [
            json.loads(request.data.decode("utf-8"))["method"]
            for request, _timeout in opener.requests
            if request.get_method() == "POST"
        ]
        self.assertEqual(
            [
                "Shelly.GetDeviceInfo",
                "Shelly.GetStatus",
                "Shelly.GetDeviceInfo",
                "Shelly.GetStatus",
                "Script.List",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.PutCode",
                "Script.List",
                "Script.Create",
                "Script.PutCode",
                "Script.PutCode",
                "Script.Start",
                "KVS.Get",
                "Script.Start",
                "Script.List",
            ],
            methods,
        )
        kvs_requests = [
            request for request, _timeout in opener.requests
            if request.get_method() == "POST" and json.loads(request.data.decode("utf-8"))["method"] == "KVS.Get"
        ]
        self.assertEqual({"key": SUPPLY_UNI_KVS_KEY}, json.loads(kvs_requests[0].data.decode("utf-8"))["params"])
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "Wifi.", "Mqtt.", "Bluetooth.", "Virtual.")
        self.assertFalse(any(any(fragment in method for fragment in forbidden_fragments) for method in methods))

    def test_supply_uni_source_uses_p0016_contract(self):
        root = Path(__file__).resolve().parents[4] / "src" / "shelly" / "supply_uni"
        publisher = (root / "supply_uni_pub.js").read_text(encoding="utf-8")
        refresher = (root / "supply_uni_refresh.js").read_text(encoding="utf-8")

        self.assertIn("supply_uni_pub", publisher)
        self.assertIn("tele.supply_uni", publisher)
        self.assertIn("voltmeter:100", publisher)
        self.assertIn("temperature:102", publisher)
        self.assertIn("HTTP.POST", publisher)
        self.assertIn("KVS.Set", publisher)
        self.assertIn("supply_uni_refresh", refresher)
        self.assertIn("supply_uni_pub", refresher)
        self.assertNotIn("g2.", publisher)
        self.assertNotIn("g2.", refresher)
        forbidden_fragments = ("Switch.", "Relay.", "Cover.", "MQTT.", "Wifi.", "Bluetooth.")
        self.assertFalse(any(fragment in publisher + refresher for fragment in forbidden_fragments))

    def test_tool_uses_standard_library_imports_only(self):
        package_root = Path(__file__).resolve().parents[4] / "src" / "mac" / "tools" / "shelly_live"
        allowed_roots = {
            "__future__",
            "argparse",
            "concurrent",
            "dataclasses",
            "json",
            "pathlib",
            "time",
            "typing",
            "urllib",
        }

        for path in package_root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertLessEqual(imports, allowed_roots, path)


if __name__ == "__main__":
    unittest.main()
