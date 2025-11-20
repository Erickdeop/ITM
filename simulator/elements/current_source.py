from __future__ import annotations
from dataclasses import dataclass
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

    def max_node(self) -> int:
        return max(self.a, self.b)

    def _value(self, t: float) -> float:
        if not self.is_ac:
            return self.dc
        return self.dc + self.amp*math.cos(2*math.pi*self.freq*t + math.radians(self.phase_deg))

    def stamp_dc(self, G, I):
        val = self._value(0.0)  # corrente
        I[self.a] += val        # entra em a
        I[self.b] -= val        # sai por b
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method):
        val = self._value(t)
        I[self.a] += val
        I[self.b] -= val
        return G, I, state


