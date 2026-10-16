"""Final-image EFFECT qualification through exported controller/Drift APIs.

No private or constprop symbol is called. Native replies and plant observations
are synthetic; this verifies compiled control decisions, not physical dynamics.
"""
import struct, os


def qualify_public_effect(u, call):
    thermal_offset = int(os.environ.get("PROCON_TEST_SUPPLY_LIMIT_CC", "4000")) - 4000
    assert thermal_offset in (0, 500)
    payload, measurement, command = 0x2000e900, 0x2000e000, 0x2000e600
    tx_type, tx_data, rx_data = 0x2000e700, 0x2000e710, 0x2000e800
    native = {"power": 1, "mode": 2, "flow": 3050, "dhw": 5200}
    time = 0
    supply, hz, power = 3300 + thermal_offset, 30, 4000
    refresh_water = refresh_hz = True
    writes = []
    call("drift", "tele_init")
    call("mode", "ctl_init")
    call("service", "svc_init")

    def state():
        return call("mode", "ctl_read", 256)

    def accept(data, observe=False):
        u.mem_write(payload, bytes(data))
        call("drift", "tele_accept", payload)
        if observe:
            call("mode", "ctl_observe", payload, time)

    def native_reply(query):
        data = bytearray(16)
        data[0] = query
        if query == 0x26:
            data[3], data[4], data[6] = native["power"], 2, native["mode"]
            data[8:10] = struct.pack(">H", native["dhw"])
        elif query == 9:
            data[5:7] = struct.pack(">H", native["flow"])
        else:
            assert query == 0x28
        return data

    def feedback():
        # A fresh aggregate deliberately cannot erase an old independent source.
        u.mem_write(measurement, struct.pack(
            "<4i2I4HB3x", power, power, power, supply,
            0, 60000, 0, 12, 2, hz, 1))
        call("mode", "ctl_feedback", measurement)

    def sources():
        # Independent A3 observations at the ordinary45s cadence, through the
        # exported service parser rather than writing its private RAM.
        if time % 45000 == 0:
            for _ in range(6):
                call("service", "svc_start_cycle")
                assert call("service", "svc_due", time, tx_type)
                code = u.mem_read(tx_type, 1)[0]
                call("service", "svc_sent", time)
                reply = bytes([0xa3, 0, code, 2, hz if code in (16,17) else 0, 0]) + bytes(10)
                u.mem_write(payload, reply)
                assert call("service", "svc_reply", payload, time, 1)
        if refresh_hz:
            accept(bytes([4, hz]) + bytes(14))
        if refresh_water:
            data = bytearray(16)
            data[0] = 0x0c
            data[1:3] = struct.pack(">H", supply)
            data[4:6] = struct.pack(">H", supply - 300)
            accept(data)
        accept(native_reply(0x26), True)
        accept(native_reply(0x28), True)

    def beat():
        nonlocal time
        call("drift", "tele_tick", 500)
        call("service", "svc_tick", 500, time + 500)
        time += 500
        if time % 5000 == 0:
            sources()
        feedback()
        if call("mode", "ctl_next", tx_type, tx_data, time):
            kind = u.mem_read(tx_type, 1)[0]
            request = bytes(u.mem_read(tx_data, 16))
            if kind == 0x41:
                flags = request[1]
                previous = native["flow"]
                # EFFECT may change mode/target, never silently stop the pump.
                assert flags in (8, 0x80, 0x88), (time, request)
                if flags & 8:
                    native["mode"] = request[6]
                if flags & 0x80:
                    native["flow"] = int.from_bytes(request[10:12], "big")
                writes.append((time, flags, previous, native["flow"], supply))
                u.mem_write(rx_data, bytes(16))
                assert call("mode", "ctl_reply", 0x61, rx_data, 1, time)
            else:
                assert kind == 0x42
                reply = native_reply(request[0])
                u.mem_write(rx_data, bytes(reply))
                assert call("mode", "ctl_reply", 0x62, rx_data, 16, time)
                accept(reply)
        assert native["power"] == 1
        assert not call("mode", "ctl_read", 260), (time, state(), call("mode", "ctl_read", 260))

    def run(duration):
        end = time + duration
        while time < end:
            beat()
            assert state() in (1, 2, 3, 4), (time, state())

    def await_state(expected):
        for _ in range(80):
            if state() == expected:
                return
            beat()
        raise AssertionError(("public controller deadline", expected, state(), time))

    sources()
    feedback()
    u.mem_write(command, struct.pack("<8H", 0xc076, 1, 5, 6000, 5500, 1800, 1, 3))
    assert call("mode", "ctl_submit", command, time) == 0
    await_state(4)
    assert native["mode"] == 1 and native["flow"] == 4300 + thermal_offset
    assert writes[0][1] == 0x88
    assert call("mode", "ctl_read", 258) == 1
    run(90000)

    # A persistently hot plant needs genuine reductions despite a power deficit.
    # The ramp itself, not a thermal-triggered AUTO/OFF, is the intended response.
    await_state(4)  # do not misclassify a pre-existing cold transaction as hot
    supply = 3950 + thermal_offset
    sources()
    hot_start, initial_hot = len(writes), native["flow"]
    run(1200000)
    hot_writes = writes[hot_start:]
    downward = [event for event in hot_writes if event[3] < event[2]]
    assert downward and native["flow"] == 3850 + thermal_offset and native["flow"] < initial_hot
    for event in hot_writes:
        stamp, flags, before, after, actual = event
        assert flags == 0x80 and max(before - 100, min(before, actual - 100)) <= after <= before
    for a, b in zip(downward, downward[1:]):
        assert b[0] - a[0] >= 30000
    assert state() == 4 and native["mode"] == 1

    # Cooling releases the constraint through ordinary bounded target updates.
    await_state(4)
    supply = 3800 + thermal_offset
    sources()
    cooling_start = len(writes)
    run(300000)
    assert native["flow"] > 4000 + thermal_offset, (native, [call("mode","ctl_read",i) for i in range(308,320)])
    for stamp, flags, before, after, actual in writes[cooling_start:]:
        assert flags == 0x80 and before - 50 <= after <= before + 200

    # A raw source remains usable below60s, but fresh aggregate power cannot
    # promote it to the quick path: any gas is limited to0.5C per minute.
    supply = 3300 + thermal_offset
    for missing in ("hz", "water"):
        refresh_hz = refresh_water = True
        sources()
        run(45000)
        refresh_hz = missing != "hz"
        refresh_water = missing != "water"
        run(20000)  # enter15..59s aging band; earlier transactions may finish
        await_state(4)
        old_count, old_target = len(writes), native["flow"]
        run(30000)
        aged_writes = writes[old_count:]
        assert native["flow"] <= old_target + 50
        assert all(event[1] == 0x80 and event[2] - 100 <= event[3] <= event[2] + 50
                   for event in aged_writes)

    refresh_hz = refresh_water = True
    sources()
    await_state(4)
    before_writes = len(writes)
    u.mem_write(command, struct.pack("<8H", 0xc076, 2, 5, 5000, 5500, 180, 1, 3))
    assert call("mode", "ctl_submit", command, time) == 0
    assert call("mode", "ctl_read", 323) == 5000 and call("mode", "ctl_read", 309) == 4511
    assert call("mode", "ctl_read", 258) == 2 and call("mode", "ctl_read", 270) == 3050
    assert native["mode"] == 1 and len(writes) == before_writes
    u.mem_write(command, struct.pack("<8H", 0xc072, 3, 1, 0, 0, 0, 0, 2))
    assert call("mode", "ctl_submit", command, time) == 0
    await_state(0)
    assert native == {"power": 1, "mode": 2, "flow": 3050, "dhw": 5200}
    assert call("mode", "ctl_read", 258) == 3
    assert not call("mode", "ctl_read", 261)
    assert call("mode", "ctl_read", 267) == 1
    print("Thermal qualification policy:", 4000 + thermal_offset)
    print("PASS actual ARM public EFFECT: atomic entry/readback, hot1C/30s taper and bounded negative margin, no pump-off, bounded cooling release, independent aged-source best effort and exact AUTO restoration")
