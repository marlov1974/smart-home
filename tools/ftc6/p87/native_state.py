"""FTC20.01 native timer and heating limiter fragments, offline only.

Numeric state names deliberately preserve unresolved physical meanings. This is
not a compressor/plant simulator. See continuation.md for ROM execution proof.
"""
from dataclasses import dataclass, field
from model import TimerWord

@dataclass(frozen=True)
class TimerDescriptor:
    mask: int
    accelerated_step: int
    threshold: int

HISTORY70 = TimerDescriptor(2, 60, 600)  # 83BCA -> 16D0
HISTORY50 = TimerDescriptor(2, 60, 180)  # 83BD0 -> 16D2

def timer_event(timer, descriptor, mask, accelerated=False):
    """A3298. Overflow in accelerated mode leaves count unchanged."""
    if descriptor.mask & mask and timer.word & 0x8000 and timer.word < 0xffff:
        step = descriptor.accelerated_step if accelerated else 1
        if 0xffff - timer.word >= step:
            timer.word += step

@dataclass
class NativeClock:
    """A3204/A3216: interrupt counts, no assumed physical crystal frequency.

TB2: reload9999, f8TIMAB. 40 interrupts generate one pending event. A stalled
main loop coalesces events; it does not recover lost counts from wall time.
"""
    interrupt_count: int = 0
    pending: bool = False
    dividers: list = field(default_factory=lambda: [0, 0, 0, 0])

    def interrupt(self):
        self.interrupt_count += 1
        if self.interrupt_count > 39:
            self.interrupt_count = 0
            self.pending = True

    def consume(self):
        if not self.pending:
            return 0
        self.pending = False
        mask = 1
        for i, threshold in enumerate((10, 100, 600, 3000)):
            self.dividers[i] += 1
            if self.dividers[i] >= threshold:
                self.dividers[i] = 0
                mask |= 2 << i
        return mask

@dataclass
class History70:
    """AC79A -> 3E02; enabled by AC16C for profiles0/2, not profile1."""
    state: int = 0
    timer: TimerWord = field(default_factory=TimerWord)

    def evaluate(self, *, enabled, error, phase_3d07, previous_phase_3e01):
        if not enabled:
            self.state = 255
        if self.state == 0:
            self.timer.clear()
            if previous_phase_3e01 != 2 and phase_3d07 == 2 and error < 200:
                self.state = 1
        elif self.state == 1:
            self.timer.clear()
            if phase_3d07 != 2:
                self.state = 2
                self.timer.reset_start()
        elif self.state == 2:
            self.timer.resume()
            if self.timer.status(HISTORY70.threshold) == 2:
                self.state = 0
            if phase_3d07 == 2:  # Overrides expiry on the same invocation.
                self.timer.clear()
                self.state = 1 if error < 200 else 0
        else:
            self.timer.clear()
            self.state = 0
        return self.state

@dataclass
class History50:
    """AC880 -> 3E05; enabled by AC16C only for profile1."""
    state: int = 0
    timer: TimerWord = field(default_factory=TimerWord)

    def evaluate(self, *, enabled, error, phase_3d07, mode_4927,
                 value_3da4, threshold_3944):
        expired = self.timer.status(HISTORY50.threshold) == 2
        if not enabled:
            self.state = 0
            self.timer.clear()
        elif self.state == 0:
            self.timer.clear()
            if mode_4927 == 2 and error <= 200 and value_3da4 < threshold_3944:
                self.state = 1
                self.timer.resume()
        elif expired or phase_3d07 == 2 or mode_4927 != 2:
            self.state = 0
            self.timer.clear()
        return self.state

def heating_limit(*, cap_4989=None, history70=0, history50=0,
                  room_start_limit=False, special_limit=None, zone_not_ready=False):
    """AC16C priority, LAST matching predicate wins (not a min reduction).

Caller must supply independently evaluated gates, including profile/mode gates.
Room-start cap30 does not apply to fixed-flow mode3915=1.
"""
    cap = 100 if cap_4989 is None else cap_4989
    if history70 == 2: cap = 70
    if history50 == 1: cap = 50
    if room_start_limit: cap = 30
    if special_limit is not None: cap = special_limit
    if zone_not_ready: cap = 0
    return cap

def final_limit(heating, setting, peer):
    """AC9A8 writes both05FE and3935, unsigned byte inputs."""
    return min(100, heating & 255, setting & 255, peer & 255)

def limit_code(value, personality=0x10):
    """99B8A, ROM82406/8241C. Physical percent meaning not asserted."""
    index = min(10, (value & 255) // 10)
    if personality == 0x10: return 10 - index
    if personality == 0: return (10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0)[index]
    return 0

@dataclass
class FixedFlowLimits:
    """Qualified AC16C fixed-flow branch,3915=1,single circuit,zone ready.

Special4911 modes, room control and two-zone handovers are outside this wrapper.
Targets/feedback are already accepted, signed centidegrees. The limit subtraction
uses signed32 and has no25C target floor (unlike A1ED8's demand lookup).
"""
    history70: History70 = field(default_factory=History70)
    history50: History50 = field(default_factory=History50)
    previous_phase: int = 0

    def event(self, mask, accelerated=False):
        timer_event(self.history70.timer,HISTORY70,mask,accelerated)
        timer_event(self.history50.timer,HISTORY50,mask,accelerated)

    def evaluate(self, target, feedback, *, profile, phase, held_error=None,
                 mode_4927=0, value_3da4=0, threshold_3944=0,
                 setting_limit=100, peer_limit=100):
        from model import signed16
        if profile not in (0,1,2): raise ValueError('Unqualified profile')
        if profile==2 and held_error is None: raise ValueError('Profile2 needs3947')
        error=signed16(held_error) if profile==2 else signed16(target)-signed16(feedback)
        s70=self.history70.evaluate(enabled=profile!=1,error=error,
              phase_3d07=phase,previous_phase_3e01=self.previous_phase)
        s50=self.history50.evaluate(enabled=profile==1,error=error,
              phase_3d07=phase,mode_4927=mode_4927,value_3da4=value_3da4,
              threshold_3944=threshold_3944)
        self.previous_phase=phase  # ABE44 stores after evaluating the chain.
        native=heating_limit(history70=s70,history50=s50)
        output=final_limit(native,setting_limit,peer_limit)
        return dict(error_cC=error,native_limit=native,final_limit=output,
                    limit_code=limit_code(output),history70=s70,history50=s50,
                    actual_hz='UNKNOWN')
