from __future__ import annotations
from dataclasses import dataclass
import numpy as np, math
from .base import Element, TimeMethod
from typing import ClassVar

@dataclass
class VoltageSource(Element):
    a: int
    b: int
    dc: float = 0.0
    amp: float = 0.0
    freq: float = 0.0
    phase_deg: float = 0.0
    is_ac: bool = False
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b)

    def _value(self, t: float) -> float:
        if not self.is_ac:
            return self.dc
        return self.dc + self.amp*math.cos(2*math.pi*self.freq*t + math.radians(self.phase_deg))

    def _augment(self, G: np.ndarray, I: np.ndarray):
        n = G.shape[0]
        G2 = np.zeros((n+1, n+1)); G2[:n,:n] = G
        I2 = np.zeros((n+1,)); I2[:n] = I
        return G2, I2

    def _stamp_common(self, G: np.ndarray, I: np.ndarray, val: float):
        G, I = self._augment(G, I)
        n = G.shape[0]-1; k = n
        G[self.a, k] += 1; G[self.b, k] -= 1
        G[k, self.a] += 1; G[k, self.b] -= 1
        I[k] += val
        return G, I

    def stamp_dc(self, G: np.ndarray, I: np.ndarray):
        return self._stamp_common(G, I, self._value(0.0))

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self._stamp_common(G, I, self._value(t))
        return G, I, state
