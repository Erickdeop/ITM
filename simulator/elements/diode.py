from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

from .base import Element
from typing import ClassVar

@dataclass
class Diode(Element):
    a: int
    b: int
    # Standard diode parameters
    Is: float = 3.7751345e-14  # Saturation Current
    Vt: float = 0.025          # Termic tension (25mV)
    is_nonlinear: ClassVar[bool] = True  # Diode is nonlinear

    def max_node(self) -> int:
        return max(self.a, self.b)

    def _get_norton_equivalent(self, Vd: float) -> Tuple[float, float]:
        """
        Calculate conductance and equivalent current source for the diode
        Uses Shockley equation of linearization
        """
        # Safe clamp
        if Vd > 0.9:
            Vd = 0.9
            print("\033[93mWarning:\033[00m Diode voltage clamped to 0.9V for numerical stability.")

        # Conductance calculation
        try:
            exp_val = np.exp(Vd / self.Vt)
        except OverflowError:
            exp_val = np.exp(0.9 / self.Vt) # Safe Fallback

        Gd = (self.Is * exp_val) / self.Vt

        # Nothon equivalent current source
        # I_eq = Is * (exp(Vd/Vt) - 1) - Gd * Vd
        I_real = self.Is * (exp_val - 1)
        I_eq = I_real - (Gd * Vd)

        return I_eq, Gd

    def stamp_dc(self, 
                 G: np.ndarray, 
                 I: np.ndarray, 
                 x_guess: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray]:
        
        if x_guess is None:
            raise RuntimeError("\033[91mDiode requer o solver Newton-Raphson (x_guess != None).\033[00m")

        # Estimate voltage across the diode
        V_d = x_guess[self.a] - x_guess[self.b]

        # Get Norton equivalent parameters
        I_eq, Gd = self._get_norton_equivalent(V_d)

        # Stamp the conductance matrix G and current vector I
        G[self.a, self.a] += Gd; G[self.b, self.b] += Gd
        G[self.a, self.b] -= Gd; G[self.b, self.a] -= Gd

        I[self.a] -= I_eq 
        I[self.b] += I_eq 

        return G, I

    def stamp_transient(self, G, I, state, t, dt, method, x_guess: np.ndarray):
        # No memory elements, same as DC
        G, I = self.stamp_dc(G, I, x_guess)
        return G, I, state