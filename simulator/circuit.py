from __future__ import annotations
import argparse
import numpy as np

from .parser import parse_netlist
from .engine import solve_dc, solve_tran
from .elements.base import TimeMethod


class Circuit:
    def __init__(self, netlist_path: str):
        # Data holds the parsed netlist
        self.data = parse_netlist(netlist_path)

    # ------------------------ DC ------------------------
    def run_dc(self, desired_nodes=None, nr_tol: float = 1e-8, v0_vector=None):
        n = self.data.max_node + 1
        
        if desired_nodes is None:
            desired_nodes = list(range(1, n))

        if v0_vector is None:
            v0_vector = np.zeros(n)

        return solve_dc(
            self.data,
            nr_tol,
            v0_vector,
            desired_nodes
        )

    # --------------------- TRANSIENT ---------------------
    def run_tran(
        self,
        desired_nodes=None,
        nr_tol: float = 1e-8,
        v0_vector=None
    ):
        ts = self.data.transient
        if not ts.enabled:
            raise RuntimeError(
                "\033[31mMissing Settings:\33[0mA netlist não possui configuração de transiente (.TRAN)."
            )

        n = self.data.max_node + 1
        if desired_nodes is None:
            desired_nodes = list(range(1, n))

        if v0_vector is None:
            v0_vector = np.zeros(n)

        method_map = {
            "BE": TimeMethod.BACKWARD_EULER,
            "FE": TimeMethod.FORWARD_EULER,
            "TRAP": TimeMethod.TRAPEZOIDAL,
        }
        method = method_map.get(ts.method.upper(), TimeMethod.BACKWARD_EULER)


        return solve_tran(
            self.data,
            ts.t_stop,
            ts.dt,
            nr_tol,
            v0_vector,
            desired_nodes,
            method,
        )
    
    def print(self):
        print(f"\n==> CIRCUIT ELEMENTS - MAX NODES={self.data.max_node}")
        for elem in self.data.elements:
            print("  -", elem)
        # Se quiser, pode imprimir também as configs de transiente:
        ts = self.data.transient
        if ts.enabled:
            print(
                f"Transient settings: t_stop={ts.t_stop}, dt={ts.dt}, method={ts.method},"
                f" internal step={ts.intetnal_steps}, uic={ts.uic}\n"
            )


# ======================================================
#                        CLI
# ======================================================

