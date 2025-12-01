from __future__ import annotations
import argparse
import numpy as np

from .parser import parse_netlist
from .engine import solve_dc, solve_tran
from .elements.base import TimeMethod


class Circuit:
    def __init__(self, netlist_path: str):
        # Apenas lê o netlist. Nada de self.data.sim
        self.data = parse_netlist(netlist_path)

    # ------------------------ DC ------------------------
    def run_dc(self, desired_nodes, nr_tol: float = 1e-8, v0_vector=None):
        n = self.data.max_node + 1

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
        desired_nodes,
        nr_tol: float = 1e-8,
        v0_vector=None
    ):
        ts = self.data.transient
        if not ts.enabled:
            raise RuntimeError(
                "\033[31mMissing Settings:\33[0mA netlist não possui configuração de transiente (.TRAN)."
            )

        n = self.data.max_node + 1

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
        print(f"\nCIRCUIT ELEMENTS - MAX NODES={self.data.max_node}")
        for elem in self.data.elements:
            print("  -", elem)
        print("\n")
        # Se quiser, pode imprimir também as configs de transiente:
        ts = self.data.transient
        if ts.enabled:
            print(
                f"TRANSIENT: t_stop={ts.t_stop}, dt={ts.dt}, "
                f"method={ts.method}, internal={ts.intetnal_steps}, uic={ts.uic}"
            )


# ======================================================
#                        CLI
# ======================================================
def _cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("--netlist", required=True)
    parser.add_argument("--nr_tol", type=float, default=1e-8)
    parser.add_argument("--nodes", nargs="+", type=int, default=[1])
    parser.add_argument("--guide", type=str) # existing .sim file path to print alongsige

    args = parser.parse_args()

    circuit = Circuit(args.netlist)
    if __debug__:
        circuit.print()

    if circuit.data.transient.enabled:
        t, out = circuit.run_tran(
            args.nodes,
            nr_tol=args.nr_tol,
        )

        print("TRAN points:", len(t))
        for i, node in enumerate(args.nodes):
            print(f"Node {node} first samples:", out[i, :10].tolist())
    else:
        # Análise DC
        result = circuit.run_dc(args.nodes, nr_tol=args.nr_tol)
        print("DC Result:", dict(zip(args.nodes, result.tolist())))


if __name__ == "__main__":
    _cli()
