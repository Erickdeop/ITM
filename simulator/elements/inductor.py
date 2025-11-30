from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .base import Element, TimeMethod
from typing import ClassVar

@dataclass
class Inductor(Element):
    a: int
    b: int
    L: float
    i0: float = 0.0 # initial condition (current)
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b)

    def _augment(self, G: np.ndarray, I: np.ndarray):
        n = G.shape[0]
        G2 = np.zeros((n+1,n+1)); G2[:n,:n]=G
        I2 = np.zeros((n+1,)); I2[:n]=I
        return G2, I2

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        # In DC, inductor is short circuit
        G, I = self._augment(G, I)
        n = G.shape[0]-1
        k = n
        G[self.a, k] += 1; G[self.b, k] -= 1
        G[k, self.a] += 1; G[k ,self.b] -= 1
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        v_prev = state.get('v_prev', 0.0)
        i_prev = state.get('i_prev', self.i0)

        G, I = self._augment(G, I)
        n = G.shape[0] - 1
        k = n
        
        G[self.a, k] += 1; G[self.b, k] -= 1
        G[k, self.a] += 1; G[k, self.b] -= 1
        
        if method == TimeMethod.BACKWARD_EULER:
            R = self.L / dt
            G[k, k] -= R
            I[k] -= R * i_prev
        elif method == TimeMethod.FORWARD_EULER:
            pass
        else:
            R = 2.0 * self.L / dt
            G[k, k] -= R 
            I[k] -= R * i_prev + v_prev
        return G, I, state
