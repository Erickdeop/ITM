from __future__ import annotations
import numpy as np
from scipy import linalg
from .elements.base import TimeMethod
from .newton import newton_solve
from typing import Tuple, Optional, List, Dict, Any
from simulator.plotting.plot_utils import load_sim_file, plot_simulation

# Elements that add extra variables in MNA (new line in matrix and vector)

def _get_mna_var_count(elem) -> int:
    """Quantas variáveis MNA extras esse elemento adiciona."""
    if not getattr(elem, "is_mna", False):
        return 0

    # Caso especial: CCVS costuma adicionar 2 variáveis (corrente de controle + de saída)
    if elem.__class__.__name__ == "CCVS":
        return 2

    # Se o elemento expõe explicitamente quantas variáveis MNA usa
    if hasattr(elem, "mna_variables"):
        try:
            n = int(elem.mna_variables())
            if n > 0:
                return n
        except Exception:
            pass

    # Caso padrão: 1 variável MNA
    return 1

def _get_total_var_count(data):
    """
    Calculates the total number of variables in the MNA system
    (max_node + 1) + (extra MNA variables).
    
    Note: Most MNA elements add 1 variable, but CCVS adds 2 variables.
    """
    n_extra = 0
    for elem in data.elements:
        n_extra += _get_mna_var_count(elem)
    return data.max_node + 1 + n_extra

def _build_mna_system(
    data, 
    x_guess_red: np.ndarray, 
    analysis_context: str, 
    t: float = 0.0, 
    dt: float = 0.0, 
    method: Optional[TimeMethod] = None, 
    states: Optional[List[Dict[str, Any]]] = None 
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build auxiliary MNA matrix (G, I) given a guess vector x_guess
    Used as callback for newton_solve.
    """

    # To be sure the correct parameters are passed
    if analysis_context == "TRAN" and (method is None or states is None):
        raise ValueError("Análise TRAN requer 'method' e 'states'.")
    
    # Get total size, including extra MNA variables
    n_total = _get_total_var_count(data)
    
    # Initialize G and I
    n_nodes = data.max_node + 1
    G = np.zeros((n_nodes, n_nodes))
    I = np.zeros(n_nodes)
    
    # Build full guess vector including node 0
    x_full = np.concatenate(([0.0], x_guess_red))

    for idx, elem in enumerate(data.elements):
        
        if analysis_context == "TRAN":
            # Redundant, but for the Type Checker.
            if method is None or states is None:
                raise ValueError("Análise TRAN requer 'method' e 'states'.")
                
            # If the element has stamp_transient, use it. Else, fallback to DC stamp.
            if hasattr(elem, "stamp_transient"):
                G, I, states[idx] = elem.stamp_transient(
                    G, I, states[idx], t, dt, method, x_full
                )
            else:
                G, I = elem.stamp_dc(G, I, x_full)
        
        elif analysis_context == "DC":
            G, I = elem.stamp_dc(G, I, x_full)
        #if __debug__:
        #    print(f"==> Stamped element: {elem}\n{G}\nI={I}")

    # Remove 0th row and column (node 0)
    return G[1:, 1:], I[1:]

from typing import Dict, Tuple, List

def build_mna_index_map(data) -> Dict[Tuple[int, str], int]:
    """
    Maps (element_index, variable_type) -> global index in x_full.

    variable_type:
      - "i"      : single current variable for the element (default MNA current)
      - "i_out"  : output current (CCVS)
      - "i_ctrl" : control current (CCVS)
    """
    mna_map: Dict[Tuple[int, str], int] = {}

    # In x_full we have:
    #   index 0           -> ground (node 0)
    #   indices 1..max_node -> node voltages
    #   indices max_node+1.. -> MNA extra variables (currents, etc.)
    idx = data.max_node + 1

    for elem_idx, elem in enumerate(data.elements):
        if not getattr(elem, "is_mna", False):
            continue

        cls_name = elem.__class__.__name__

        if cls_name == "CCVS":
            # First index: control current
            mna_map[(elem_idx, "i_ctrl")] = idx
            # Second index: output current
            mna_map[(elem_idx, "i_out")] = idx + 1
            idx += 2
        else:
            n_vars = _get_mna_var_count(elem)
            if n_vars == 1:
                mna_map[(elem_idx, "i")] = idx
            else:
                # Generic case if any element uses more than 1 MNA variable
                for k in range(n_vars):
                    mna_map[(elem_idx, f"i{k}")] = idx + k
            idx += n_vars

    return mna_map


# ============================================================
#                      DC SOLVER
# ============================================================
def solve_dc(data, nr_tol, v0_vector, desired_nodes, 
             max_nr_iter: int = 50, max_nr_guesses: int = 100):
    """
    Solve DC analysis.

    Uses Newton-Raphson because of non linear elements only if needed:
    - LINEAR circuit: Uses direct solve (faster, single matrix inversion)
    - NONLINEAR circuit: Uses Newton-Raphson iteration
    
    Parameters:
    -----------
    data : ParsedNetlist
        Parsed circuit netlist
    nr_tol : float
        Newton-Raphson tolerance
    v0_vector : Optional[np.ndarray]
        Initial voltage vector
    desired_nodes : List[int]
        Nodes to return in output
    max_nr_iter : int
        Maximum NR iterations per guess (N, typically 20-50)
    max_nr_guesses : int
        Maximum number of random guess attempts (M, typically 100)
    """
    # Get system total size, including extra MNA variables
    n_total = _get_total_var_count(data)
    
    # Define initial guess.
    if v0_vector is not None and len(v0_vector) == n_total:
         x0_red = v0_vector[1:].copy()
    else:
         x0_red = np.zeros(n_total - 1)
    
    # Check if circuit has nonlinear elements
    if data.has_nonlinear_elements:
        # NONLINEAR
        print("[DC Analysis] Using Newton-Raphson (nonlinear circuit)")
        
        def build_mna(x_guess_red: np.ndarray):
            return _build_mna_system(
                data, 
                x_guess_red, 
                analysis_context="DC"
            )
        
        try:
            x_red = newton_solve(build_mna, x0_red, tol=nr_tol, 
                                max_iter=max_nr_iter, max_guesses=max_nr_guesses)
        except Exception as e:
            raise RuntimeError(f"NR falhou na análise DC: {e}")
    else:
        # LINEAR
        print("[DC Analysis] Using direct solve (linear circuit)")
        
        try:
            G, I = _build_mna_system(data, x0_red, analysis_context="DC")
            x_red = linalg.solve(G, I)
        except Exception as e:
            raise RuntimeError(f"Solução direta falhou na análise DC: {e}")

    # Reconstruct full x with node 0
    x = np.concatenate(([0.0], x_red))

    # TODO: Every node should be a desired node?
    # If so, we can return the full x vector
    if desired_nodes is not None:
        return np.array([x[node] for node in desired_nodes])
    else:
        return x

# ============================================================
#              TRANSIENT SOLVER (NR + BE/TRAP/FE)
# ============================================================

def solve_tran(
    data,
    total_time,
    dt,
    nr_tol,
    v0_vector,
    desired_nodes,
    method,
    max_nr_iter: int = 50,
    max_nr_guesses: int = 100,
):
    """
    Solve transient (time-domain) analysis using Newton-Raphson.

    Parameters
    ----------
    data : NetlistOOP
        Parsed netlist object (elements + max_node).
    total_time : float
        Final simulation time (seconds).
    dt : float
        Time step (seconds).
    nr_tol : float
        Newton-Raphson tolerance.
    v0_vector : np.ndarray | None
        Initial node voltages. Must have at least (max_node + 1) entries.
        Extra MNA variables are initialized to zero.
    desired_nodes : list[int]
        Node indices whose voltages will be stored in the output.
    method : TimeMethod
        Time integration method (BE, FE, TRAP).
    max_nr_iter : int
        Maximum NR iterations per guess.
    max_nr_guesses : int
        Maximum number of random guess attempts.
    """

    if total_time <= 0.0 or dt <= 0.0:
        raise ValueError("total_time and dt must be positive for TRAN analysis.")

    # Number of time samples (include t = 0)
    steps = int(total_time / dt) + 1
    times = np.linspace(0.0, total_time, steps)

    # One state dict per element (for capacitors, inductors, etc.)
    states: List[Dict[str, Any]] = [dict() for _ in data.elements]

    # Output matrix: each row is a node, each column is a time sample
    out = np.zeros((len(desired_nodes), steps))

    # Total number of unknowns in the MNA system (nodes + extra MNA variables)
    n_total = _get_total_var_count(data)

    # ------------------ initial guess vector ------------------
    # x[0] is always ground = 0. Other entries are nodes + MNA variables.
    if v0_vector is None:
        x = np.zeros(n_total)
    else:
        if len(v0_vector) < n_total:
            x = np.zeros(n_total)
            x[: len(v0_vector)] = v0_vector
        else:
            x = v0_vector.copy()

    # ------------------------------------------------------------------
    # Prepare mapping from elements to global MNA indices (currents, etc.)
    # ------------------------------------------------------------------
    mna_index_map = build_mna_index_map(data)

    # Prepare structures to store currents over time:
    #   current_traces: name -> np.array(steps)
    #   tracked_currents: list of (element_index, signal_name, mna_key_or_None)
    #
    # If mna_key is None, current is taken from element state (e.g. Inductor).
    # If mna_key is "i", "i_out", etc, current is read directly from x.
    current_traces: Dict[str, np.ndarray] = {}
    tracked_currents: List[Tuple[int, str, Optional[str]]] = []

    for elem_idx, elem in enumerate(data.elements):
        cls_name = elem.__class__.__name__

        # Inductor current is handled via its state (i_prev)
        if cls_name == "Inductor":
            signal_name = f"J{elem.name}"
            current_traces[signal_name] = np.zeros(steps)
            tracked_currents.append((elem_idx, signal_name, None))

        # Generic MNA elements (voltage sources, controlled sources, opamp, etc.)
        elif getattr(elem, "is_mna", False):
            # Choose which MNA variable represents the "main" current
            if cls_name == "CCVS":
                mna_key = "i_out"  # output branch current
            else:
                mna_key = "i"      # default single current variable

            key = (elem_idx, mna_key)
            if key in mna_index_map:
                signal_name = f"J{elem.name}"
                current_traces[signal_name] = np.zeros(steps)
                tracked_currents.append((elem_idx, signal_name, mna_key))

    # ============================================================
    #                       TIME LOOP
    # ============================================================
    for ti, t in enumerate(times):

        # Keep previous solution as initial guess for NR
        x_prev = x.copy()

        # ---------- build MNA system for this time step ----------
        def build_mna(x_guess_red: np.ndarray):
            """
            Callback for Newton-Raphson:
            receives x_guess without node 0 (reduced vector) and
            returns (G_red, I_red) for the current time step.
            """
            G_red, I_red = _build_mna_system(
                data,
                x_guess_red,
                analysis_context="TRAN",
                t=t,
                dt=dt,
                method=method,   # TimeMethod
                states=states,   # List[Dict[str, Any]]
            )
            return G_red, I_red

        # ---------- solve non-linear MNA with NR ----------
        try:
            # We remove node 0 (always 0) from the unknown vector
            x_red = newton_solve(
                build_mna,
                x_prev[1:],
                tol=nr_tol,
                max_iter=max_nr_iter,
                max_guesses=max_nr_guesses,
            )
        except RuntimeError as e:
            # Add time information to the error for easier debugging
            raise RuntimeError(
                f"NR não convergiu em t={t:.5e}s na análise transiente.\n{e}"
            ) from e

        # Reconstruct full solution vector including node 0
        x = np.concatenate(([0.0], x_red))

        # ---------- update element states (capacitors, inductors, ...) ----------
        for idx, elem in enumerate(data.elements):
            st = states[idx]

            # Reactive elements need to store previous voltages/currents
            # TODO: Generalize this with an interface in the elements in
            # order to avoid class name checks (better OOP)

            # We avoid importing specific classes here; use class name instead
            if elem.__class__.__name__ == "Capacitor":
                # Store capacitor voltage for next step
                st["v_prev"] = x[elem.a] - x[elem.b]

            elif elem.__class__.__name__ == "Inductor":
                # Inductor current is stored in "i_prev"
                if method == TimeMethod.BACKWARD_EULER:
                    # i_new = i_old + (dt/L) * v
                    i_old = st.get("i_prev", elem.i0)
                    v = x[elem.a] - x[elem.b]
                    i_new = i_old + (dt / elem.L) * v
                    st["i_prev"] = i_new

                elif method == TimeMethod.TRAPEZOIDAL:
                    # i_new = i_old + (dt/(2L)) * (v_new + v_old)
                    i_old = st.get("i_prev", elem.i0)
                    v_old = st.get("v_prev", 0.0)
                    v = x[elem.a] - x[elem.b]
                    i_new = i_old + (dt / (2 * elem.L)) * (v + v_old)
                    st["i_prev"] = i_new
                    st["v_prev"] = v

            states[idx] = st

        # ---------- store desired node voltages ----------
        for j, node in enumerate(desired_nodes):
            out[j, ti] = x[node]

        # ---------- store currents (state / MNA) ----------
        for elem_idx, signal_name, mna_key in tracked_currents:
            elem = data.elements[elem_idx]

            # State-based current (e.g., Inductor)
            if mna_key is None:
                st = states[elem_idx]
                if elem.__class__.__name__ == "Inductor":
                    i_val = st.get("i_prev", getattr(elem, "i0", 0.0))
                else:
                    # Fallback, should not normally happen
                    v = x[getattr(elem, "a", 0)] - x[getattr(elem, "b", 0)]
                    i_val = 0.0
                current_traces[signal_name][ti] = i_val

            # MNA-based current (voltage sources, controlled sources, opamp, etc.)
            else:
                key = (elem_idx, mna_key)
                idx_global = mna_index_map.get(key)
                if idx_global is not None and 0 <= idx_global < len(x):
                    current_traces[signal_name][ti] = x[idx_global]
                else:
                    # If for some reason we cannot map, store 0.0 as a safe default
                    current_traces[signal_name][ti] = 0.0

    # At this point:
    #   - 'out' contains node voltages vs time
    #   - 'current_traces' contains currents of inductors and MNA elements vs time
    return times, out, current_traces