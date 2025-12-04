from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Tuple, Optional, ClassVar
import numpy as np

class TimeMethod(Enum):
    BACKWARD_EULER = auto()
    FORWARD_EULER = auto()
    TRAPEZOIDAL = auto()

@dataclass
class Element:
    is_mna: ClassVar[bool] = False # Tells if the element adds MNA variables (new lines in matrix and vector)
    is_nonlinear: ClassVar[bool] = False # Tells if the element is nonlinear (requires Newton-Raphson)

    def max_node(self) -> int:
        raise NotImplementedError

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess=None) -> Tuple[np.ndarray, np.ndarray]:
        return G, I

    def stamp_transient(self, G: np.ndarray, I: np.ndarray, state: Dict[str, Any], t: float, dt: float, method: TimeMethod):
        return G, I, state
