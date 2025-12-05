from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, ClassVar
import numpy as np, math
from .base import Element, TimeMethod

@dataclass
class CurrentSource(Element):
    a: int
    b: int
    dc: float = 0.0
    amp: float = 0.0
    freq: float = 0.0
    phase_deg: float = 0.0
    is_ac: bool = False
    source_type: str = "DC"  # "DC", "AC", "SIN", "PULSE"
    sin_params: Optional[Dict[str, float]] = None
    pulse_params: Optional[Dict[str, float]] = None

    def max_node(self) -> int:
        return max(self.a, self.b)

    def get_value_at(self, time: float) -> float:
        """
        Get current value at specific time.
        """
        if self.source_type == "DC":
            return self.dc
        elif self.source_type == "AC":
            return self.dc + self.amp * math.cos(2*math.pi*self.freq*time + math.radians(self.phase_deg))
        elif self.source_type == "SIN":
            return self._sin_value(time)
        elif self.source_type == "PULSE":
            return self._pulse_value(time)
        else:
            return self.dc

    def _sin_value(self, time: float) -> float:
        """
        Format: SIN(I_offset I_amplitude freq delay damping phase)
        i(t) = I_offset + I_amplitude * exp(-damping*(t-delay))
            * sin(2*pi*freq*(t-delay) + phase)
        """
        if self.sin_params is None:
            return self.dc
        
        offset    = self.sin_params.get("offset", 0.0)
        amplitude = self.sin_params.get("amplitude", 0.0)
        freq      = self.sin_params.get("freq", 0.0)
        delay     = self.sin_params.get("delay", 0.0)
        damping   = self.sin_params.get("damping", 0.0)
        phase     = self.sin_params.get("phase", 0.0)   # vem em graus da netlist

        # converte sempre pra radianos de forma explícita
        phase_rad = math.radians(phase)

        if time < delay:
            return offset + amplitude * math.sin(phase_rad)

        t_eff = time - delay
        damping_factor = math.exp(-damping * t_eff) if damping > 0 else 1.0

        return offset + amplitude * damping_factor * math.sin(
            2 * math.pi * freq * t_eff + phase_rad
        )

    def _pulse_value(self, time: float) -> float:
        """
        Format: PULSE(i1 i2 delay rise_time fall_time pulse_width period)
        States:
        - t < delay: i1
        - delay <= t < delay+rise_time: linear rise from i1 to i2
        - delay+rise_time <= t < delay+rise_time+pulse_width: i2
        - delay+rise_time+pulse_width <= t < delay+rise_time+pulse_width+fall_time: linear fall from i2 to i1
        - t >= delay+rise_time+pulse_width+fall_time: i1 (and repeat for next period)
        """
        if self.pulse_params is None:
            return self.dc
        
        i1 = self.pulse_params.get("i1", 0.0)
        i2 = self.pulse_params.get("i2", 0.0)
        delay = self.pulse_params.get("delay", 0.0)
        rise_time = self.pulse_params.get("rise_time", 0.0)
        fall_time = self.pulse_params.get("fall_time", 0.0)
        pulse_width = self.pulse_params.get("pulse_width", 0.0)
        period = self.pulse_params.get("period", 0.0)
        
        # before delay, return i1
        if time < delay:
            return i1
        
        if period > 0:
            t_local = (time - delay) % period
        else:
            t_local = time - delay
        
        if t_local < rise_time:
            # rising
            if rise_time > 0:
                return i1 + (i2 - i1) * (t_local / rise_time)
            else:
                return i2
        elif t_local < rise_time + pulse_width:
            # high state
            return i2
        elif t_local < rise_time + pulse_width + fall_time:
            # falling
            if fall_time > 0:
                t_fall = t_local - rise_time - pulse_width
                return i2 - (i2 - i1) * (t_fall / fall_time)
            else:
                return i1
        else:
            # low state
            return i1

    def _value(self, t: float) -> float:
        """Maintains retrocompatibility"""
        return self.get_value_at(t)

    def stamp_dc(self, G, I, x_guess=None):
        val = self._value(0.0)  # current flows from a to b
        I[self.a] -= val        # current leaves node a
        I[self.b] += val        # current enters node b
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        val = self._value(t)   # current flows from a to b
        I[self.a] -= val       # current leaves node a
        I[self.b] += val       # current enters node b
        return G, I, state


