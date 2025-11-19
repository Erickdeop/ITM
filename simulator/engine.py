from __future__ import annotations
import numpy as np
from scipy import linalg
from .elements.base import TimeMethod


# ============================================================
#                      DC SOLVER
# ============================================================
def solve_dc(data, nr_tol, v0_vector, desired_nodes):
    n = data.max_node + 1
    G = np.zeros((n, n))
    I = np.zeros(n)

    for e in data.elements:
        G, I = e.stamp_dc(G, I)

    # Remove nó 0
    x_red = linalg.solve(G[1:, 1:], I[1:])
    x = np.concatenate(([0.0], x_red))

    return np.array([x[node] for node in desired_nodes])


# ============================================================
#              TRANSIENT SOLVER (NR + BE/TRAP/FE)
# ============================================================
def solve_tran(data, total_time, dt, nr_tol, v0_vector, desired_nodes, method):

    steps = int(total_time / dt) + 1
    times = np.linspace(0, total_time, steps)

    # estados por elemento
    states = [dict() for _ in data.elements]

    out = np.zeros((len(desired_nodes), steps))

    # condição inicial
    x = v0_vector.copy()

    # ------------------------------------------------------------
    # LOOP PRINCIPAL DE TEMPO
    # ------------------------------------------------------------
    for ti, t in enumerate(times):

        x_prev = x.copy()
        converged = False

        # --------------------------------------------------------
        #          NEWTON–RAPHSON
        # --------------------------------------------------------
        for it in range(100):

            n = data.max_node + 1
            G = np.zeros((n, n))
            I = np.zeros(n)

            # estampar todos os elementos
            for idx, elem in enumerate(data.elements):
                if hasattr(elem, "stamp_transient"):
                    G, I, states[idx] = elem.stamp_transient(
                        G, I, states[idx], t, dt, method
                    )
                else:
                    G, I = elem.stamp_dc(G, I)

            # resolver
            try:
                x_red = linalg.solve(G[1:, 1:], I[1:])
                x_new = np.concatenate(([0.0], x_red))
            except Exception:
                raise RuntimeError(f"Sistema singular em t={t}")

            # ----------------------------------------------------
            #      ⚠️ AJUSTE CRÍTICO DE DIMENSÃO
            # ----------------------------------------------------
            if len(x_prev) != len(x_new):
                x_prev = np.resize(x_prev, len(x_new))

            # teste NR
            if np.linalg.norm(x_new - x_prev, np.inf) < nr_tol:
                converged = True
                x = x_new.copy()
                break

            x_prev = x_new.copy()

        if not converged:
            raise RuntimeError(f"NR não convergiu em t={t}")

        # --------------------------------------------------------
        # Atualizar estados (capacitor/indutor)
        # --------------------------------------------------------
        for idx, elem in enumerate(data.elements):

            st = states[idx]

            # capacitor
            if elem.__class__.__name__ == "Capacitor":
                st["v_prev"] = x[elem.a] - x[elem.b]

            # indutor
            elif elem.__class__.__name__ == "Inductor":
                if method == TimeMethod.BACKWARD_EULER:
                    R = elem.L / dt
                    st["i_prev"] = (x[elem.a] - x[elem.b]) / R

            states[idx] = st

        # salvar saída
        for j, node in enumerate(desired_nodes):
            out[j, ti] = x[node]

    return times, out
