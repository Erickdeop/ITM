from dataclasses import dataclass
from typing import Tuple
import numpy as np

from .base import Element 

@dataclass
class NonLinearResistor(Element):
    a: int
    b: int
    V_points: np.ndarray 
    I_points: np.ndarray

    def max_node(self) -> int:  
        return max(self.a, self.b)

    def _get_current_and_conductance(self, Vab: float) -> Tuple[float, float]:
        """
        Calculate the equivalent current and conductance for the Non-Linear Resistor
        """
        # Get Vab and find the segment
        if Vab <= self.V_points[0]:
            idx = 0
        elif Vab >= self.V_points[-1]:
            idx = len(self.V_points) - 2
        else:
            idx = np.searchsorted(self.V_points, Vab) - 1

        # Get points of the segment
        V_i, I_i = self.V_points[idx], self.I_points[idx]
        V_i1, I_i1 = self.V_points[idx+1], self.I_points[idx+1]
        
        # Get the equivalent conductance (G_eq) as the slope of the segment
        if V_i1 == V_i:
            G_eq = 0.0
        else:
            G_eq = (I_i1 - I_i) / (V_i1 - V_i)
        
        # Calculate the equivalent current source (I_eq) for the Norton model
        I_resistor = I_i + G_eq * (Vab - V_i)
        
        # I_NR = I_resistor - G_eq * Vab
        I_nr = I_resistor - G_eq * Vab
        
        return I_nr, G_eq

    def stamp_dc(self, 
                 G: np.ndarray, 
                 I: np.ndarray, 
                 x_guess: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray]:
        """
        DC analisis stamping for Non-Linear Resistor.
        Uses Norton equivalent model based on current voltage guess.
        Where:
        - G_eq is the equivalent conductance matrix
        - I_N is the equivalent current source vector
        - x_guess is necessary, guess vector from Newton-Raphson solver
        """

        if x_guess is None:
            # If no guess is provided, we cannot linearize the resistor
            raise RuntimeError(
                "\033[91mNonLinearResistor requer o solver Newton-Raphson (x_guess != None).\033[00m"
            )
        
        V_ab = x_guess[self.a] - x_guess[self.b]
        
        I_N, G_eq = self._get_current_and_conductance(V_ab)

        G[self.a, self.a] += G_eq; G[self.b, self.b] += G_eq
        G[self.a, self.b] -= G_eq; G[self.b, self.a] -= G_eq

        I[self.a] -= I_N
        I[self.b] += I_N

        return G, I
    
    def stamp_transient(self, G, I, state, t, dt, method, x_guess: np.ndarray):
        G, I = self.stamp_dc(G, I, x_guess)
        return G, I, state