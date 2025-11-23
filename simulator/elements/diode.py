from .base import Element
from dataclasses import dataclass
import numpy as np

@dataclass
class Diode(Element):
    a: int
    b: int

    def max_node(self) -> int:
        return max(self.a, self.b)

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None):
        return G, I

    def stamp_transient(self, G:np.ndarray, I:np.ndarray, state, t, dt, method, x_guess=None):
        return G, I, state
