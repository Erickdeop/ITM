from __future__ import annotations
import numpy as np

from dataclasses import dataclass, field
from typing import List

from .engine import solve_dc, solve_tran
from .elements.base import TimeMethod

@dataclass
class TransientSettings:
    enabled: bool = False   # [1]
    t_stop: float = 0.0     # [2]
    dt: float = 0.0         # [3]
    method: str = "BE"      # [4] BE, FE or TRAP
    intetnal_steps: int = 0 # [5] 
    uic: bool = True        # [6] use initial conditions: Optional

@dataclass
class NetlistOOP:
    elements: List[object]
    max_node: int
    transient: TransientSettings = field(default_factory=TransientSettings)
    has_nonlinear_elements: bool = False  # True if circuit contains nonlinear elements

class Circuit:
    def __init__(self, data: NetlistOOP):
        self.data = data
        self.name: str
        self.last_tran_time = None          # np.ndarray | None
        self.last_tran_signals = None       # dict[str, np.ndarray] | None

    # ------------------------ DC ------------------------
    def run_dc(self, desired_nodes=None, nr_tol: float = 1e-8, v0_vector=None,
               max_nr_iter: int = 50, max_nr_guesses: int = 100):
        """        
        desired_nodes : List[int], optional
            Nodes to include in output
        nr_tol : float
            Newton-Raphson tolerance (default: 1e-8)
        v0_vector : np.ndarray, optional
            Initial voltage vector
        max_nr_iter : int
            Maximum NR iterations per guess (N, typically 20-50)
        max_nr_guesses : int
            Maximum number of random guess attempts (M, typically 100)
        """
        n = self.data.max_node + 1
        
        if desired_nodes is None:
            desired_nodes = list(range(1, n))

        if v0_vector is None:
            v0_vector = np.zeros(n)

        return solve_dc(
            self.data,
            nr_tol,
            v0_vector,
            desired_nodes,
            max_nr_iter,
            max_nr_guesses
        )

    # --------------------- TRANSIENT ---------------------
    def run_tran(
        self,
        desired_nodes=None,
        total_time: float | None = None,
        dt: float | None = None,
        method: str | TimeMethod | None = None,
        nr_tol: float = 1e-8,
        v0_vector=None,
    ):
        """
        Run transient analysis using the netlist's transient settings
        as default, but allowing overrides via parameters.

        Parameters
        ----------
        desired_nodes : list[int] | None
            Nodes whose voltages will be returned and stored as Node_k signals.
            If None, uses all nodes from 1..max_node.
        total_time : float | None
            Final simulation time. If None, uses self.data.transient.t_stop.
        dt : float | None
            Time step. If None, uses self.data.transient.dt.
        method : str | TimeMethod | None
            Integration method. If None, uses self.data.transient.method.
        nr_tol : float
            Newton-Raphson tolerance.
        v0_vector : np.ndarray | None
            Initial guess for node voltages + MNA variables (optional).

        Returns
        -------
        times : np.ndarray
            Time vector.
        out : np.ndarray
            Matrix of node voltages (len(desired_nodes) x n_steps).
        """

        # --------- resolve desired nodes ---------
        if desired_nodes is None:
            # by default, use all physical nodes except ground (0)
            desired_nodes = list(range(1, self.data.max_node + 1))

        # --------- resolve transient settings (use netlist defaults when None) ---------
        tran = getattr(self.data, "transient", None)

        if total_time is None:
            if tran is None or tran.t_stop is None:
                raise ValueError("total_time not provided and no transient.t_stop defined in netlist.")
            total_time = tran.t_stop

        if dt is None:
            if tran is None or tran.dt is None:
                raise ValueError("dt not provided and no transient.dt defined in netlist.")
            dt = tran.dt
        
        method_map = {
            "BE": TimeMethod.BACKWARD_EULER,
            "FE": TimeMethod.FORWARD_EULER,
            "TRAP": TimeMethod.TRAPEZOIDAL,
        }

        if method is None:
            if tran is not None and getattr(tran, "method", None):
                method = tran.method
            else:
                method = "BE"

        # Convert method string to TimeMethod enum if needed
        if isinstance(method, str):
            method = method_map.get(self.data.transient.method.upper(), TimeMethod.BACKWARD_EULER)

        # --------- call engine solver ---------
        times, out, current_traces = solve_tran(
            self.data,
            total_time=total_time,
            dt=dt,
            nr_tol=nr_tol,
            v0_vector=v0_vector,
            desired_nodes=desired_nodes,
            method=method,
        )

        # --------- build signal dictionary: nodes + currents ---------
        signals: dict[str, np.ndarray] = {}

        # Node voltages
        for j, node in enumerate(desired_nodes):
            signals[f"Node_{node}"] = out[j, :]

        # Currents from engine (inductors, voltage sources, controlled sources, opamp, etc.)
        signals.update(current_traces)

        # --------- store for later use (.sim export, plotting, etc.) ---------
        self.last_tran_time = times
        self.last_tran_signals = signals

        return times, out
    
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

