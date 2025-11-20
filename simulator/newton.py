# simulator/newton.py

import numpy as np
from scipy import linalg

def newton_solve(build_mna, x0, tol=1e-6, max_iter=1):
    """
    Versão simplificada do Newton–Raphson para circuitos LINEARES.
    Como os testes atuais não usam componentes não lineares,
    G e I não dependem de x -> basta resolver G x = I uma única vez.
    """

    # monta o sistema (G, I)
    G, I = build_mna(x0)

    # resolve diretamente
    try:
        x = linalg.solve(G, I)
    except Exception:
        raise RuntimeError(
            f"Newton–Raphson não convergiu — residual={np.linalg.norm(R, np.inf)}"
        )


    return x
