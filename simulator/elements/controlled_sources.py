from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .base import Element
from typing import ClassVar


@dataclass
class VCVS(Element):
    a: int  # positive output node
    b: int  # negative output node
    c: int  # positive control node
    d: int  # negative control node
    gain: float  # voltage gain (Av)
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b, self.c, self.d)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        
        n = G.shape[0]
        x_idx = n  # index for new MNA variable
        
        # Expand matrices
        G_new = np.zeros((n+1, n+1))
        G_new[:n, :n] = G
        I_new = np.zeros(n+1)
        I_new[:n] = I
        
        # Stamp output nodes
        G_new[self.a, x_idx] = 1.0
        G_new[self.b, x_idx] = -1.0
        
        # Stamp control equation: v_out = gain * v_control
        # v_a - v_b - gain*(v_c - v_d) = 0
        G_new[x_idx, self.a] = -1.0
        G_new[x_idx, self.b] = 1.0
        G_new[x_idx, self.c] = self.gain
        G_new[x_idx, self.d] = -self.gain
        
        return G_new, I_new

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self.stamp_dc(G, I)
        return G, I, state


@dataclass
class CCCS(Element):
    a: int  # positive output node
    b: int  # negative output node
    c: int  # positive control node
    d: int  # negative control node
    gain: float  # current gain (Ai)
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b, self.c, self.d)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        n = G.shape[0]
        x_idx = n
        
        # Expand matrices
        G_new = np.zeros((n+1, n+1))
        G_new[:n, :n] = G
        I_new = np.zeros(n+1)
        I_new[:n] = I
        
        # Output current: i_out = gain * i_control
        G_new[self.a, x_idx] = self.gain
        G_new[self.b, x_idx] = -self.gain
        
        # Control current measurement (adds voltage source at control nodes)
        G_new[self.c, x_idx] = 1.0
        G_new[self.d, x_idx] = -1.0
        
        # Control equation: v_c - v_d = 0 (short circuit for current measurement)
        G_new[x_idx, self.c] = -1.0
        G_new[x_idx, self.d] = 1.0
        
        return G_new, I_new

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self.stamp_dc(G, I)
        return G, I, state


@dataclass
class VCCS(Element):
    a: int  # positive output node
    b: int  # negative output node
    c: int  # positive control node
    d: int  # negative control node
    gm: float  # transconductance (Siemens)
    is_mna: ClassVar[bool] = False

    def max_node(self) -> int:
        return max(self.a, self.b, self.c, self.d)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        # Output current injections
        G[self.a, self.c] += self.gm
        G[self.a, self.d] -= self.gm
        G[self.b, self.c] -= self.gm
        G[self.b, self.d] += self.gm
        
        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self.stamp_dc(G, I)
        return G, I, state


@dataclass
class CCVS(Element):
    a: int  # positive output node
    b: int  # negative output node
    c: int  # positive control node
    d: int  # negative control node
    rm: float  # transresistance (Ohms)
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b, self.c, self.d)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        n = G.shape[0]
        i_control_idx = n      # control current variable
        i_output_idx = n + 1   # output current variable
        
        # Expand matrices for 2 additional variables
        G_new = np.zeros((n+2, n+2))
        G_new[:n, :n] = G
        I_new = np.zeros(n+2)
        I_new[:n] = I
        
        # KCL: Control current enters at c, exits at d
        G_new[self.c, i_control_idx] = 1.0
        G_new[self.d, i_control_idx] = -1.0
        
        # KCL: Output current enters at a, exits at b
        G_new[self.a, i_output_idx] = 1.0
        G_new[self.b, i_output_idx] = -1.0
        
        # Control branch constraint: v_c - v_d = 0 (short circuit for measurement)
        G_new[i_control_idx, self.c] = 1.0
        G_new[i_control_idx, self.d] = -1.0
        
        # Output voltage constraint: v_a - v_b = rm * i_control
        G_new[i_output_idx, self.a] = 1.0
        G_new[i_output_idx, self.b] = -1.0
        G_new[i_output_idx, i_control_idx] = -self.rm
        
        return G_new, I_new

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):
        G, I = self.stamp_dc(G, I)
        return G, I, state