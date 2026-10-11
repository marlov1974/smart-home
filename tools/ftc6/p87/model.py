"""Offline FTC20.01 partial transcription. No device I/O and no Hz predictor.

Inputs are already selected/accepted raw centidegrees, not a wire transaction.
See evidence.json for scope. UNKNOWN is intentionally contagious at boundaries.
"""
from dataclasses import dataclass
UNKNOWN = 'UNKNOWN'
HEAT_TABLE = tuple(zip(range(-200, 251, 50), range(2900, 2449, -50))) + ((32767, 2400),)

def signed16(n):
    n &= 65535
    return n - 65536 if n & 32768 else n

def truncdiv(n, d):
    return (abs(n) // d) * (-1 if n < 0 else 1)

def temperature_byte(value):
    """9A336/9A39E: signed input, clamp then round upward in 50 raw units."""
    return (min(8000, max(0, signed16(value))) + 49) // 50

def error_byte(error):
    """99F5A: addition wraps as a word BEFORE sign extension/division."""
    return min(255, max(0, truncdiv(signed16(error + 4000), 50)))

def lookup(error):
    e = signed16(error)
    return next(value for threshold, value in HEAT_TABLE if e <= threshold)

def pump_step(request, phase, dhw_step, heating_step, mode_3d07=0,
              state_3a02=0, state_3ad2=0, correction_49c7=0):
    """AF400 + AF452. Request/phase/gates must come from upstream caller."""
    step = (3 if request == 2 else
            (dhw_step if phase in (9, 10) and mode_3d07 != 2 and state_3a02 != 2
             else heating_step) if request == 1 else 0)
    if request == 1 and state_3ad2 == 2 and 2 <= correction_49c7 <= 7:
        step = max(2, step - (correction_49c7 - 2))
    return step

@dataclass
class TimerWord:
    """Generic helper semantics only; caller supplies count, NEVER seconds."""
    word: int = 0
    def reset_start(self): self.word = 0x8000  # A330E
    def clear(self): self.word = 0            # A3322
    def resume(self): self.word |= 0x8000     # A3334
    def pause(self): self.word &= 0x7fff      # A3354
    def status(self, threshold):             # A3392
        return 0 if not self.word & 0x8000 else (2 if self.word & 0x7fff >= threshold else 1)


def evaluate(target, feedback, *, valid=True, age_ms=0, phase=8,
             profile_0900=0, held_error=None, override_4911=0,
             special_target=False):
    """Restricted single-circuit heating branch; no assumed scheduler or acceptance."""
    result = dict(actual_hz=UNKNOWN, stop_restart=UNKNOWN, native_memory=UNKNOWN,
                  timing=UNKNOWN, target_cC=target, feedback_cC=feedback)
    if not valid or age_ms is None or age_ms < 0 or age_ms > 60000:
        return dict(result, status=UNKNOWN, reason='invalid or stale analysis input; 60s is replay policy, not native timeout')
    if phase != 8 or target is None or feedback is None or special_target:
        return dict(result, status=UNKNOWN, reason='outside qualified ordinary heating branch')
    error = signed16(max(signed16(target), 2500) - signed16(feedback))
    if profile_0900 == 2:
        if held_error is None:
            return dict(result, status=UNKNOWN, reason='profile2 requires held error 3947')
        error = signed16(held_error)
    demand = 2700 if override_4911 == 2 else lookup(error)
    return dict(result, status='PARTIAL', error_cC=error, table_value_cC=demand,
                virtual_temperature_byte=(min(3950, max(800, demand))-800)//50,
                error_byte=error_byte(error), target_byte=temperature_byte(target),
                feedback_byte=temperature_byte(feedback), local_lookup_memory='none')


def water_balance_delta(power_w, litres_min):
    """Assumed pure water rho=1kg/L, cp=4180J/kg/K; not Mitsubishi control."""
    if litres_min <= 0: return UNKNOWN
    return power_w / (4180 * litres_min / 60)
