from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .base import Element, TimeMethod

@dataclass
class Capacitor(Element):
    a: int
    b: int
    C: float

    def max_node(self) -> int:
        return max(self.a, self.b)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray):
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        v_prev = state.get('v_prev', 0.0)
        i_prev = state.get('i_prev', 0.0)

        if method == TimeMethod.BACKWARD_EULER:
            Gc = self.C/dt
            G[self.a,self.a]+=Gc; G[self.b,self.b]+=Gc
            G[self.a,self.b]-=Gc; G[self.b,self.a]-=Gc
            I[self.a]+=Gc*v_prev; I[self.b]+=-Gc*v_prev

        elif method == TimeMethod.FORWARD_EULER:
            i_eq = self.C*(0.0 - v_prev)/dt
            I[self.a]-=i_eq; I[self.b]+=i_eq

        else:  # TRAPEZOIDAL
            Gc = 2 * self.C / dt

            G[self.a, self.a] += Gc
            G[self.b, self.b] += Gc
            G[self.a, self.b] -= Gc
            G[self.b, self.a] -= Gc

            Ieq = i_prev + Gc * v_prev

            I[self.a] += Ieq
            I[self.b] -= Ieq

        return G, I, state
