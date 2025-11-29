import numpy as np
from scipy import linalg
from typing import Callable, Tuple


def newton_solve(
    build_mna: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]], 
    x0: np.ndarray, 
    tol: float = 1e-6, 
    max_iter: int = 25 # Market default
) -> np.ndarray:
    """
    Newton-Raphson Solver for Non-Linear Systems.

    The MNA linearized system is given by: G_k * Delta_x = -R_k
    Where:
    - G_k is the Jacobian Matrix (Tangent Conductance)
    - R_k is the residual vector (G_k * x_k - I_k)
    - I_K is the Current Source Vector (including linearized Norton sources)
    """

    x_k = x0.copy()  # Initial guess
    
    for k in range(max_iter):
        G_k, I_k = build_mna(x_k)
        
        # R = G*x - I
        R_k = G_k @ x_k - I_k
        
        # Check convergence. Residual should be close to zero. If so, return. 
        residual_norm = np.linalg.norm(R_k, np.inf)
        if residual_norm < tol:
            return x_k
        
        # Solve linearized system for increment (Delta_x)
        try:
            delta_x = linalg.solve(G_k, -R_k)
        except linalg.LinAlgError as e:
            # If matrix is singular, raise an error
            raise RuntimeError(
                f"NR falhou na iteração {k}. Matriz Jacobiana (G) singular. "
                f"Resíduo atual: {residual_norm:.3e}"
            ) from e

        # Update solution vector (New Guess)
        x_k = x_k + delta_x
        
    # If loop ends without convergence, raise an error
    raise RuntimeError(
        f"Newton-Raphson não convergiu após {max_iter} iterações. "
        f"Último resíduo: {residual_norm:.3e} (Tolerância: {tol:.1e})"
    )