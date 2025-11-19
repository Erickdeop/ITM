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
        total_time: float,
        dt: float,
        method: TimeMethod = TimeMethod.TRAPEZOIDAL,
        nr_tol: float = 1e-8,
        v0_vector=None
    ):
        n = self.data.max_node + 1

        if v0_vector is None:
            v0_vector = np.zeros(n)

        return solve_tran(
            self.data,
            total_time,
            dt,
            nr_tol,
            v0_vector,
            desired_nodes,
            method
        )


# ======================================================
#                        CLI
# ======================================================
def _cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("--netlist", required=True)
    parser.add_argument("--analysis", choices=["DC", "TRAN"], required=True)
    parser.add_argument("--nodes", nargs="+", type=int, default=[1])
    parser.add_argument("--nr_tol", type=float, default=1e-8)
    parser.add_argument("--total_time", type=float, default=1e-3)
    parser.add_argument("--dt", type=float, default=1e-5)
    parser.add_argument("--method", choices=["BE", "FE", "TRAP"], default="TRAP")

    args = parser.parse_args()

    circuit = Circuit(args.netlist)

    method_map = {
        "BE": TimeMethod.BACKWARD_EULER,
        "FE": TimeMethod.FORWARD_EULER,
        "TRAP": TimeMethod.TRAPEZOIDAL,
    }
    method = method_map[args.method]

    if args.analysis == "DC":
        result = circuit.run_dc(args.nodes, nr_tol=args.nr_tol)
        print("DC Result:", dict(zip(args.nodes, result.tolist())))

    else:
        t, out = circuit.run_tran(
            args.nodes,
            total_time=args.total_time,
            dt=args.dt,
            method=method,
            nr_tol=args.nr_tol,
        )

        print("TRAN points:", len(t))
        for i, node in enumerate(args.nodes):
            print(f"Node {node} first samples:", out[i, :10].tolist())


if __name__ == "__main__":
    _cli()
