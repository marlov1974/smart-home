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
