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

def solve_tran(data, total_time: float, dt: float, nr_tol: float, v0_vector: np.ndarray, desired_nodes: list[int], method: TimeMethod):
    npts = int(total_time/dt)+1
    tspace = np.linspace(0.0, total_time, npts, endpoint=True)
    states = [dict() for _ in data.elements]
    out = np.zeros((len(desired_nodes), npts))
    for ti, t in enumerate(tspace):
        n0 = data.max_node + 1
        G = np.zeros((n0,n0)); I = np.zeros(n0)
        for idx, e in enumerate(data.elements):
            G, I, states[idx] = e.stamp_transient(G, I, states[idx], t, dt if ti>0 else 1e-30, method)
        e_red = linalg.solve(G[1:,1:], I[1:])
        e_all = np.concatenate(([0.0], e_red))
        for idx, e in enumerate(data.elements):
            st = states[idx]
            if hasattr(e,'a') and hasattr(e,'b'):
                st['v_prev'] = float(e_all[e.a] - e_all[e.b])
            states[idx] = st
        for j, node in enumerate(desired_nodes):
            out[j, ti] = e_all[node]
    return tspace, out
