from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, Tuple
import numpy as np

class TimeMethod(Enum):
    BACKWARD_EULER = auto()
    FORWARD_EULER = auto()
    TRAPEZOIDAL = auto()

@dataclass
class Element:
    def max_node(self) -> int:
        raise NotImplementedError

    def stamp_dc(self, G: np.ndarray, I: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return G, I

    def stamp_transient(self, G: np.ndarray, I: np.ndarray, state: Dict[str, Any], t: float, dt: float, method: TimeMethod):
        return G, I, state
