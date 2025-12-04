import numpy as np
from scipy import linalg
from typing import Callable, Tuple


def newton_solve(
    build_mna: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]], 
    x0: np.ndarray, 
    tol: float = 1e-6, 
    max_iter: int = 50, # Market default
    max_guesses: int = 100  # Maximum number of random guesses
) -> np.ndarray:
    """
    Newton-Raphson Solver for Non-Linear Systems with multiple random retries.

    The MNA linearized system is given by: G_k * Delta_x = -R_k
    Where:
    - G_k is the Jacobian Matrix (Tangent Conductance)
    - R_k is the residual vector (G_k * x_k - I_k)
    - I_K is the Current Source Vector (including linearized Norton sources)
    
    Parameters:
    -----------
    build_mna : function
        Builds the MNA system (G, I) given a guess vector
    x0 : np.ndarray
        Initial guess vector
    tol : float
        Convergence tolerance (default: 1e-6)
    max_iter : int
        Maximum iterations per guess attempt (N, normally 20-50)
    max_guesses : int
        Maximum number of random guess attempts (M, normally 100)
        
    Returns:    np.ndarray
        Converged solution vector
        
    Raises:
        If convergence fails after all attempts
    """

    n_guess_attempts = 0
    last_residual = None
    
    for n_guess_attempts in range(max_guesses):
        # Use initial guess for first attempt, random for subsequent attempts
        if n_guess_attempts == 0:
            x_k = x0.copy()
        else:
            # Generate random guess between -10V and +10V
            x_k = np.random.uniform(-10.0, 10.0, size=x0.shape)
        
        converged = False
        for k in range(max_iter):
            try:
                G_k, I_k = build_mna(x_k)
            except Exception as e:
                # If build_mna fails, this guess is invalid, try next one
                break
            
            R_k = G_k @ x_k - I_k
            
            # Check convergence. Residual should be close to zero. If it is, return 
            residual_norm = np.linalg.norm(R_k, np.inf)
            last_residual = residual_norm
            
            if residual_norm < tol:
                if n_guess_attempts > 0:
                    print(f"[NR] Convergiu na tentativa {n_guess_attempts + 1} "
                          f"após {k + 1} iterações")
                converged = True
                return x_k
            
            try:
                delta_x = linalg.solve(G_k, -R_k)
            except linalg.LinAlgError:
                # If matrix is singular, this guess is bad, try next one
                break

            # Update solution vector (New Guess)
            x_k = x_k + delta_x
        
        # If converged, we already returned. If not, continue to next guess
        if not converged and n_guess_attempts < max_guesses - 1:
            continue
    
    # If it doesn't converge, raise an error
    raise RuntimeError(
        f"Newton-Raphson não convergiu após {n_guess_attempts + 1} tentativas "
        f"com {max_iter} iterações cada. "
        f"Último resíduo: {last_residual:.3e} (Tolerância: {tol:.1e})"
    )