from dataclasses import dataclass, field
from typing import List
from .parser import NetlistOOP, TransientSettings

from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource
from .elements.nonlinear_resistor import NonLinearResistor
from .elements.diode import Diode

# ... demais elementos


@dataclass
class CircuitBuilder:
    name: str = "CIRCUITO_1"
    max_node: int = 0
    elements: List[object] = field(default_factory=list)
    transient: TransientSettings = field(default_factory=TransientSettings)

    def rename(self, new_name: str):
        self.name = new_name

    def _update_max_node(self, *nodes: int):
        self.max_node = max(self.max_node, *nodes)

    # ----------------- Add Elements -----------------
    def add_resistor(self, a: int, b: int, R: float):
        self.elements.append(Resistor(a, b, R))
        self._update_max_node(a, b)

    def add_capacitor(self, a: int, b: int, C: float, ic: float = 0.0):
        self.elements.append(Capacitor(a, b, C, ic))
        self._update_max_node(a, b)

    def add_inductor(self, a: int, b: int, L: float, ic: float = 0.0):
        self.elements.append(Inductor(a, b, L, ic))
        self._update_max_node(a, b)

    # ... add_current_source, add_voltage_source, etc

    # ---------------- Set Transient Settings -----------------
    def set_transient(self, t_stop: float, dt: float, method: str = "BE", internal_steps: int = 0, uic: bool = True):
        self.transient.t_stop = t_stop
        self.transient.dt = dt
        self.transient.method = method.upper()
        self.transient.intetnal_steps = internal_steps
        self.transient.uic = uic
    
    def enable_transient(self, enabled: bool = True):
        self.transient.enabled = enabled

    # ---- Converter para NetlistOOP ----
    def to_netlist_oop(self) -> NetlistOOP:
        return NetlistOOP(
            elements=self.elements.copy(),
            max_node=self.max_node,
            transient=self.transient,
        )
