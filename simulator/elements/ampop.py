# simulator/elements/opamp.py
from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar
import numpy as np

from .base import Element


@dataclass
class OpAmp(Element):
    
    a: int  # nó de saída +
    b: int  # nó de saída -
    c: int  # entrada +
    d: int  # entrada -
    gain: float = 1e5  # ganho alto por padrão

    # Diz ao engine que este elemento adiciona equação MNA
    is_mna: ClassVar[bool] = True

    def max_node(self) -> int:
        return max(self.a, self.b, self.c, self.d)

    def mna_variables(self) -> int:
        
        return 1
    #Estampa um opamp como um VCVS com ganho alto.
    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        
        n = G.shape[0]
        x_idx = n  # índice da nova variável MNA

        # Expande as matrizes
        G_new = np.zeros((n + 1, n + 1))
        G_new[:n, :n] = G

        I_new = np.zeros(n + 1)
        I_new[:n] = I

        # KCL nos nós de saída (corrente da fonte de tensão interna)
        G_new[self.a, x_idx] += 1.0
        G_new[self.b, x_idx] -= 1.0

        # Equação de controle do opamp:
        # v_a - v_b - gain * (v_c - v_d) = 0
        G_new[x_idx, self.a] -= 1.0
        G_new[x_idx, self.b] += 1.0
        G_new[x_idx, self.c] += self.gain
        G_new[x_idx, self.d] -= self.gain

        return G_new, I_new

    def stamp_transient(self, G, I, state, t, dt, method, x_guess=None):

        G_new, I_new = self.stamp_dc(G, I, x_guess)
        return G_new, I_new, state
