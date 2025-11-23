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
        Calcula I e G_eq (Condutância Equivalente) para a tensão Vab usando PWL.
        """
        # 1. Encontra a qual segmento Vab pertence
        if Vab <= self.V_points[0]:
            idx = 0
        elif Vab >= self.V_points[-1]:
            idx = len(self.V_points) - 2
        else:
            # Encontra o índice 'i' onde V_points[i] <= Vab < V_points[i+1]
            idx = np.searchsorted(self.V_points, Vab) - 1

        # 2. Segmento (Vi, Ii) a (Vi+1, Ii+1)
        V_i, I_i = self.V_points[idx], self.I_points[idx]
        V_i1, I_i1 = self.V_points[idx+1], self.I_points[idx+1]
        
        # 3. Calcula a Condutância (G_eq) do segmento (a derivada I/V)
        if V_i1 == V_i:
            G_eq = 0.0 # Caso extremo (linha vertical)
        else:
            G_eq = (I_i1 - I_i) / (V_i1 - V_i)
        
        # 4. Calcula a Corrente Equivalente (I_eq) para o método NR (I_eq = I - G_eq * V)
        # O modelo Norton equivalente é: I = G_eq * V + I_N
        # I_N (source) = I - G_eq * V  
        # Corrente do Elemento (I_resistor) = I_i + G_eq * (Vab - V_i)
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
        Estampa para a análise DC, dependendo da estimativa atual de x (voltages).
        A estamparia é feita pelo modelo equivalente Norton para NR:
        I_NR = G_eq * V_ab + I_N
        Onde:
        - G_eq é a condutância tangente (derivada I/V)
        - I_N é a fonte de corrente equivalente (residual)
        """

        if x_guess is None:
            # Se for chamado sem chute, significa que o solver DC LINEAR foi usado (erro)
            raise RuntimeError(
                "NonLinearResistor requer o solver Newton-Raphson (x_guess != None)."
            )
        
        V_ab = x_guess[self.a] - x_guess[self.b]
        
        # Calcula a corrente equivalente I_N e a condutância G_eq
        I_N, G_eq = self._get_current_and_conductance(V_ab)

        # Estamparia (Método MNA com modelo Norton equivalente)
        # 1. Estampar G_eq
        G[self.a, self.a] += G_eq; G[self.b, self.b] += G_eq
        G[self.a, self.b] -= G_eq; G[self.b, self.a] -= G_eq

        # 2. Estampar a fonte de corrente I_N
        I[self.a] -= I_N # Sinais: I sai do nó a
        I[self.b] += I_N # I entra no nó b

        return G, I
    
    # Em um Resistor Não-Linear, a estamparia Transiente é idêntica à DC,
    # pois não há componentes reativos (C ou L) que exijam integração temporal.
    def stamp_transient(self, G, I, state, t, dt, method, x_guess: np.ndarray):
        G, I = self.stamp_dc(G, I, x_guess)
        return G, I, state