from .base import Element
from dataclasses import dataclass
import numpy as np

@dataclass
class NonLinearResistor(Element):
    a: int
    b: int
    V1: float; I1: float
    V2: float; I2: float
    V3: float; I3: float
    V4: float; I4: float

    def max_node(self) -> int:  
        return max(self.a, self.b)
    
    def stamp_dc(self, G:np.ndarray, I:np.ndarray):
        return G, I

    def stamp_transient(self, G:np.ndarray, I:np.ndarray, state, t, dt, method, x_guess=None):
        return G, I, state
