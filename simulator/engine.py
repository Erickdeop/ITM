from __future__ import annotations
import numpy as np
from scipy import linalg
from .elements.base import TimeMethod
from .newton import newton_solve


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

    states = [dict() for _ in data.elements]
    out = np.zeros((len(desired_nodes), steps))

    n = data.max_node + 1

    # condição inicial (corrigido!)
    if v0_vector is None:
        x = np.zeros(n)
    else:
        x = v0_vector.copy()

    # ============================================
    # LOOP DE TEMPO - CORRIGIDO
    # ============================================
    for ti, t in enumerate(times):

        x_prev = x.copy()
        x_guess = x_prev.copy()

        # ---------- monta o sistema MNA ----------
        def build_mna(x_guess):

            G = np.zeros((n, n))
            I = np.zeros(n)

            for idx, elem in enumerate(data.elements):
                
                if hasattr(elem, "stamp_transient"):
                    G, I, states[idx] = elem.stamp_transient(
                        G, I, states[idx], t, dt, method, x_guess
                    )
                else:
                    G, I = elem.stamp_dc(G, I)

            # remove nó 0 (terra)
            G_red = G[1:, 1:]
            I_red = I[1:]

            return G_red, I_red

        # ---------- resolve MNA ----------
        try:
            x_red = newton_solve(build_mna, x_prev[1:], tol=nr_tol)
        except Exception:
            raise RuntimeError(f"NR não convergiu em t={t}")

        # reconstrói x com nó 0
        x = np.concatenate(([0.0], x_red))

        # ---------- atualiza estados ----------
        for idx, elem in enumerate(data.elements):

            st = states[idx]

            if elem.__class__.__name__ == "Capacitor":
                st["v_prev"] = x[elem.a] - x[elem.b]

            elif elem.__class__.__name__ == "Inductor":
                if method == TimeMethod.BACKWARD_EULER:
                    R = elem.L / dt
                    st["i_prev"] = (x[elem.a] - x[elem.b]) / R

            states[idx] = st

        # salva saída
        for j, node in enumerate(desired_nodes):
            out[j, ti] = x[node]

    return times, out

