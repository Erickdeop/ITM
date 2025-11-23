from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .base import Element, TimeMethod

@dataclass
class Resistor(Element):
    a: int
    b: int
    R: float

    def max_node(self) -> int:
        return max(self.a, self.b)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        g = 1.0/self.R
        G[self.a, self.a] += g
        G[self.b, self.b] += g
        G[self.a, self.b] -= g
        G[self.b, self.a] -= g
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self.stamp_dc(G, I)
        return G, I, state
