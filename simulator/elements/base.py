from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Tuple, Optional
import numpy as np

class TimeMethod(Enum):
    BACKWARD_EULER = auto()
    FORWARD_EULER = auto()
    TRAPEZOIDAL = auto()

@dataclass
class Element:
    is_mna: bool = field(default=False, init=False) # Tells if the element adds MNA variables (new lines in matrix and vector)

    def max_node(self) -> int:
        raise NotImplementedError

    def stamp_dc(self, G: np.ndarray, I: np.ndarray, x_guess:Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        return G, I

    def stamp_transient(self, G: np.ndarray, I: np.ndarray, state: Dict[str, Any], t: float, dt: float, method: TimeMethod):
        return G, I, state
