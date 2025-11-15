from __future__ import annotations
import numpy as np
from scipy import linalg
from .elements.base import TimeMethod
from .parser import parse_netlist

def solve_dc(data, nr_tol: float, v0_vector: np.ndarray, desired_nodes: list[int]) -> np.ndarray:
    n = data.max_node + 1
    G = np.zeros((n,n)); I = np.zeros(n)
    for e in data.elements:
        G, I = e.stamp_dc(G, I)
        n = G.shape[0]
    e_red = linalg.solve(G[1:,1:], I[1:])
    e_all = np.concatenate(([0.0], e_red))
    return np.array([e_all[node] for node in desired_nodes])

def solve_tran(data, total_time: float, dt: float,
               nr_tol: float, v0_vector: np.ndarray,
               desired_nodes: list[int], method: TimeMethod):

    # Número total de pontos do transiente
    npts = int(total_time / dt) + 1

    # Espaço de tempo
    tspace = np.linspace(0.0, total_time, npts)

    # Estado interno de cada elemento (v_prev, i_prev etc.)
    states = [dict() for _ in data.elements]

    # Matriz de saída (uma linha por nó desejado)
    out = np.zeros((len(desired_nodes), npts))

    # ================================
    # PT2 – LAÇO DE TEMPO PRINCIPAL
    # ================================
    for ti, t in enumerate(tspace):

        # Número de nós + variáveis auxiliares
        n = data.max_node + 1

        # ================================
        # PT2 – MONTAGEM DO SISTEMA LINEAR
        # ================================
        # Gx = I
        G = np.zeros((n, n))
        I = np.zeros(n)

        # Estampagem dos elementos para BE
        for idx, e in enumerate(data.elements):

            # dt especial na iteração zero (para IC)
            h = dt if ti > 0 else 1e-30

            G, I, states[idx] = e.stamp_transient(
                G, I, states[idx], t, h, method
            )

        # ================================
        # PT2 – RESOLUÇÃO DO SISTEMA
        # ================================

        # Elimina linha e coluna do terra (nó 0)
        G_reduced = G[1:, 1:]
        I_reduced = I[1:]

        # Resolve Gx = I
        sol = linalg.solve(G_reduced, I_reduced)

        # Reconstrói vetor completo incluindo GND
        full_sol = np.concatenate(([0.0], sol))

        # Atualiza estados internos
        for idx, e in enumerate(data.elements):
            if hasattr(e, "a") and hasattr(e, "b"):
                states[idx]["v_prev"] = full_sol[e.a] - full_sol[e.b]
            if "i_prev" in states[idx]:
                pass  # indutor usa isso internamente

        # ================================
        # PT2 – ARMAZENAMENTO DO RESULTADO
        # ================================
        for j, node in enumerate(desired_nodes):
            out[j, ti] = full_sol[node]

    return tspace, out