from __future__ import annotations
import argparse
import numpy as np
from .parser import parse_netlist
from .engine import solve_dc, solve_tran
from .elements.base import TimeMethod

class Circuit:
    def __init__(self, netlist_path: str):
        self.data = parse_netlist(netlist_path)

    def run_dc(self, desired_nodes, nr_tol: float = 1e-8, v0_vector=None):
        n = self.data.max_node + 1
        if v0_vector is None:
            v0_vector = np.zeros(n)
        return solve_dc(self.data, nr_tol, v0_vector, desired_nodes)

    def run_tran(self, desired_nodes, total_time: float, dt: float, method: TimeMethod = TimeMethod.TRAPEZOIDAL, nr_tol: float = 1e-8, v0_vector=None):
        n = self.data.max_node + 1
        if v0_vector is None:
            v0_vector = np.zeros(n)
        return solve_tran(self.data, total_time, dt, nr_tol, v0_vector, desired_nodes, method)

def _cli():
    p = argparse.ArgumentParser()
    p.add_argument('--netlist', required=True)
    p.add_argument('--analysis', choices=['DC','TRAN'], required=True)
    p.add_argument('--nodes', nargs='+', type=int, default=[1])
    p.add_argument('--nr_tol', type=float, default=1e-8)
    p.add_argument('--total_time', type=float, default=1e-3)
    p.add_argument('--dt', type=float, default=1e-5)
    p.add_argument('--method', choices=['BE','FE','TRAP'], default='TRAP')
    args = p.parse_args()
    ckt = Circuit(args.netlist)
    method = {'BE': TimeMethod.BACKWARD_EULER, 'FE': TimeMethod.FORWARD_EULER, 'TRAP': TimeMethod.TRAPEZOIDAL}[args.method]
    if args.analysis == 'DC':
        ans = ckt.run_dc(args.nodes, nr_tol=args.nr_tol)
        print('DC', dict(zip(args.nodes, ans.tolist())))
    else:
        t, out = ckt.run_tran(args.nodes, total_time=args.total_time, dt=args.dt, method=method, nr_tol=args.nr_tol)
        print('TRAN points:', len(t))
        for i, node in enumerate(args.nodes):
            print(f'node {node} first5:', out[i,:5].tolist())

if __name__ == '__main__':
    _cli()
