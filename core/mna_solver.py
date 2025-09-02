### Montador e resolvedor do sistema MNA ###

import numpy as np
from components.componentes import Componentes

class MNASolver:
    def __init__(self, elementos, nodemap):
        self.elementos = elementos
        self.nodemap = nodemap
        self.comp = Componentes()
        self.indutores = [e for e in elementos if e["tipo"] == "L"]
        self.Nn = nodemap.count
        self.Nx = len(self.indutores)
        self.N = self.Nn + self.Nx
        self.extra_map = {e["nome"]: self.Nn + i for i, e in enumerate(self.indutores)}

    def montar(self, h, state):
        A = np.zeros((self.N, self.N))
        b = np.zeros((self.N,))
        for e in self.elementos:
            self.comp.stamp(A, b, e, h, state, self.extra_map)
        return A, b

    def solve_dc(self):
        A, b = self.montar(None, {})
        x = np.linalg.solve(A, b)
        return x, A, b

    def solve_transient(self, h, state):
        A, b = self.montar(h, state)
        x = np.linalg.solve(A, b)
        return x, A, b

    def next_state(self, x, h, prev):
        state = dict(prev)
        for e in self.elementos:
            if e["tipo"] == "C":
                state[f"V_{e['nome']}"] = x[e["n1"]] - x[e["n2"]]
            elif e["tipo"] == "L":
                state[f"I_{e['nome']}"] = x[self.extra_map[e["nome"]]]
        return state
