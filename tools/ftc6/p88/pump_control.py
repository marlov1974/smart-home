"""P0088: pure models of selected FTC20.01 pump-level consumers.

Raw state only. No transport, physical watt calibration or complete controller.
"""
ALLOWANCE_ROWS = ((0, 29, 41, 56, 63, 63), (0, 38, 68, 105, 153, 180))


def selected_level(demand, operating_state, exclusion_a, exclusion_b,
                   dhw_level, heating_level, profile, reduction):
    if any(not isinstance(x, int) or not 0 <= x <= 255 for x in
           (demand, operating_state, exclusion_a, exclusion_b, dhw_level,
            heating_level, profile, reduction)):
        raise ValueError('raw uint8 state required')
    if demand == 2:
        return 3
    if demand != 1:
        return 0
    level = (dhw_level if operating_state in (9, 10)
             and exclusion_a != 2 and exclusion_b != 2 else heating_level)
    if profile == 2 and 2 <= reduction <= 7:
        level = max(2, level - (reduction - 2))
    return level


def accounting_allowance(level, variant, configured, enabled):
    if not 0 <= level <= 255 or not 0 <= variant <= 255 or not 0 <= configured <= 65535:
        raise ValueError('raw state out of bounds')
    value = configured
    if configured == 9999:
        value = ALLOWANCE_ROWS[int(variant > 21)][level] if level < 6 else 0
    return min(value, 200) if enabled else 0


def reduction_code(state, count):
    if not 0 <= state <= 255 or not 0 <= count <= 255:
        raise ValueError('raw uint8 state required')
    return (0 if state == 0 else 1 if state == 1 else min(count, 5) + 2
            if state == 2 else 255 if state == 3 else 0)


def reduction_allowed(reference, flow_temp, return_temp, sensor_0686,
                      flow_raw, configured_min_flow, level):
    def signed16(x):
        return ((x + 32768) & 65535) - 32768
    if any(not -32768 <= x <= 32767 for x in (reference, flow_temp, return_temp, sensor_0686)):
        raise ValueError('signed16 sensor inputs required')
    if not 0 <= flow_raw <= 65535 or not 0 <= configured_min_flow <= 255 or not 0 <= level <= 255:
        raise ValueError('unsigned input out of range')
    return (signed16(reference-flow_temp) >= 300
            and signed16(flow_temp-return_temp) >= 300
            and return_temp <= 5000 and sensor_0686 >= 1000
            and flow_raw >= 1000 and flow_raw >= configured_min_flow*100
            and level >= 3)


def sample_average(samples, previous):
    if len(samples) > 17 or any(not 0 <= x <= 0xffffffff for x in [*samples, previous]):
        raise ValueError('at most17 uint32 samples required')
    return ((sum(samples) & 0xffffffff) // len(samples)) if samples else previous


def reduction_active(configuration, phase):
    """9171A record30 phase mask; not proof of installed configuration."""
    if not 0 <= configuration <= 255 or not 0 <= phase < 14:
        raise ValueError('configuration byte and bounded phase required')
    return configuration != 0 and phase == 8


def reduction_configuration(mode_3a4a, state_3a4f, setting_07df, level_07e6,
                            flags_06d5, setting_07ee, setting_0a45,
                            flags_06d7, flags_06d4, setting_073c):
    """91FC0 -> 923BC -> 09F1 -> 917FE -> 0939, qualified FTC20.01.

    Profile2 override for this byte is FF (retain calculated value).
    ROM88EEE=0 enables publication. Not a claim about installed firmware.
    """
    values = (mode_3a4a, state_3a4f, setting_07df, level_07e6, flags_06d5,
              setting_07ee, setting_0a45, flags_06d7, flags_06d4, setting_073c)
    if any(not isinstance(v, int) or not 0 <= v <= 255 for v in values):
        raise ValueError('raw uint8 configuration required')
    return int(mode_3a4a == 0 and state_3a4f == 0 and setting_07df == 1
               and level_07e6 >= 3 and bool(flags_06d5 & 0x80)
               and setting_07ee != 1 and setting_0a45 != 1
               and not flags_06d7 & 1
               and not (flags_06d4 & 0x10 and setting_073c == 1))


def reduction_source_class(flags_06d5, flags_06d6):
    """C61F6: derive3A4F; external class names remain unqualified."""
    if any(not isinstance(v, int) or not 0 <= v <= 255 for v in (flags_06d5, flags_06d6)):
        raise ValueError('raw uint8 flags required')
    if not flags_06d5 & 0x20:
        return 0
    return 1 if flags_06d6 & 0x20 or not flags_06d5 & 0x40 else 2


def reduction_aux_inhibit(flags_06d9, state_06a5):
    """91A70: derive0A45 before any later configuration overlay."""
    if any(not isinstance(v, int) or not 0 <= v <= 255 for v in (flags_06d9, state_06a5)):
        raise ValueError('raw uint8 state required')
    return 0 if flags_06d9 & 0x10 and state_06a5 == 1 else int(bool(flags_06d9 & 8))
