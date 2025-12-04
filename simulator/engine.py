from __future__ import annotations
import numpy as np
from scipy import linalg
from .elements.base import TimeMethod
from .newton import newton_solve
from typing import Tuple, Optional, List, Dict, Any
from simulator.plotting.plot_utils import load_sim_file, plot_simulation

# Elements that add extra variables in MNA (new line in matrix and vector)

def get_total_variables(data):
    """
    Calculates the total number of variables in the MNA system
    (max_node + 1) + (extra MNA variables).
    
    Note: Most MNA elements add 1 variable, but CCVS adds 2 variables.
    """
    n_nodes = data.max_node + 1
    n_extra = 0
    
    for elem in data.elements:
        if elem.is_mna:
            # Check if this element adds more than 1 MNA variable
            if hasattr(elem, 'mna_variables'):
                n_extra += elem.mna_variables()
            elif elem.__class__.__name__ == 'CCVS':
                # CCVS adds 2 variables (control current + output current)
                n_extra += 2
            else:
                # Most elements (VoltageSource, VCVS, CCCS) add 1 variable
                n_extra += 1
            
    return n_nodes + n_extra

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
    n_total = get_total_variables(data)
    
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
    n_total = get_total_variables(data)
    
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
def solve_tran(data, total_time, dt, nr_tol, v0_vector, desired_nodes, method,
               max_nr_iter: int = 50, max_nr_guesses: int = 100):
    """
    Solve transient (over time) analysis.
    Uses Newton-Raphson.
    
    Parameters:
    -----------
    data : ParsedNetlist
        Parsed circuit netlist
    total_time : float
        Total simulation time
    dt : float
        Time step
    nr_tol : float
        Newton-Raphson tolerance
    v0_vector : Optional[np.ndarray]
        Initial voltage vector
    desired_nodes : List[int]
        Nodes to return in output
    method : TimeMethod
        Integration method (BE, FE, TRAP)
    max_nr_iter : int
        Maximum NR iterations per guess (N, typically 20-50)
    max_nr_guesses : int
        Maximum number of random guess attempts (M, typically 100)
    """

    steps = int(total_time / dt) + 1
    times = np.linspace(0, total_time, steps)

    states = [dict() for _ in data.elements]
    out = np.zeros((len(desired_nodes), steps))

    # Get system total size, including extra MNA variables
    n_total = get_total_variables(data)

    # Define initial guess vector with proper size.
    if v0_vector is None:
        x = np.zeros(n_total)
    else:
        if len(v0_vector) < n_total:
            x = np.zeros(n_total)
            x[:len(v0_vector)] = v0_vector
        else:
            x = v0_vector.copy()

    # ============================================
    # TIME LOOP
    # ============================================
    for ti, t in enumerate(times):

        x_prev = x.copy()

        # ---------- build MNA system ----------
        def build_mna(x_guess_red: np.ndarray):
            # Previous function moved to include DC analysis
            G_red, I_red = _build_mna_system(
                data, 
                x_guess_red, 
                analysis_context="TRAN", 
                t=t, 
                dt=dt, 
                method=method, # TimeMethod
                states=states  # List[Dict]
            )
            return G_red, I_red

        # ---------- solve MNA (Newton-Raphson) ----------
        # Passamos o chute inicial reduzido (sem o nó 0)
        # x_prev tem tamanho n_total. x_prev[1:] tem tamanho n_total-1.
        try:
            x_red = newton_solve(build_mna, x_prev[1:], tol=nr_tol,
                                max_iter=max_nr_iter, max_guesses=max_nr_guesses)
        except Exception as e:
            raise RuntimeError(f"NR não convergiu em t={t:.5f}s na analise transiente."
                               "\nErro: {e}")

        # reconstruct full x (with node 0)
        x = np.concatenate(([0.0], x_red))

        # ---------- update states ----------
        for idx, elem in enumerate(data.elements):
            st = states[idx]
            
            # Reactive elements need to store previous voltages/currents
            # TODO: Generalize this with an interface in the elements in 
            # order to avoid class name checks (better OOP)
            if elem.__class__.__name__ == "Capacitor":
                st["v_prev"] = x[elem.a] - x[elem.b]

            elif elem.__class__.__name__ == "Inductor":
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

        # save desired nodes
        for j, node in enumerate(desired_nodes):
            out[j, ti] = x[node]

    py_vars = {
        f"Node_{node}": out[j, :]
        for j, node in enumerate(desired_nodes)
    }

    # loading .sim
    
    return times, out