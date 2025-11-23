from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np

from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource
from .elements.nonlinear_resistor import NonLinearResistor
from .elements.diode import Diode


@dataclass
class NetlistOOP:
    elements: List[object]
    max_node: int


def parse_netlist(path: str) -> NetlistOOP:
    elems = []
    maxnode = 0

    def update_nodes(*ns):
        nonlocal maxnode
        maxnode = max(maxnode, *ns)

    with open(path, "r") as f:
        for raw in f:
            line = raw.strip()

            if not line or line.startswith("*"):
                continue

            p = line.split()
            element_type = p[0][0].upper()
            if line.startswith("."):
                continue
            # ------------------- RESISTOR -------------------
            if element_type == "R":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                elems.append(Resistor(a, b, val))
                update_nodes(a, b)

            # ------------------- CAPACITOR -------------------
            elif element_type == "C":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                elems.append(Capacitor(a, b, val))
                update_nodes(a, b)

            # ------------------- INDUCTOR -------------------
            elif element_type == "L":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                elems.append(Inductor(a, b, val))
                update_nodes(a, b)

            # ------------------- CURRENT SOURCE -------------------
            elif element_type == "I":
                a = int(p[1]); b = int(p[2])
                stype = p[3].upper()

                if stype == "DC":
                    dc = float(p[4])
                    elems.append(CurrentSource(a, b, dc=dc, is_ac=False))

                elif stype == "AC":
                    dc = float(p[4]) if len(p) > 4 else 0.0
                    amp = float(p[5]) if len(p) > 5 else 0.0
                    freq = float(p[6]) if len(p) > 6 else 0.0
                    phase = float(p[7]) if len(p) > 7 else 0.0

                    elems.append(CurrentSource(
                        a, b,
                        dc=dc, amp=amp, freq=freq,
                        phase_deg=phase, is_ac=True
                    ))
                else:
                    raise ValueError(f"Formato inválido para corrente: {p}")

                update_nodes(a, b)

            # ------------------- VOLTAGE SOURCE -------------------
            elif element_type == "V":
                a = int(p[1]); b = int(p[2])
                stype = p[3].upper()

                if stype == "DC":
                    dc = float(p[4])
                    elems.append(VoltageSource(a, b, dc=dc, is_ac=False))

                elif stype == "AC":
                    dc = float(p[4]) if len(p) > 4 else 0.0
                    amp = float(p[5]) if len(p) > 5 else 0.0
                    freq = float(p[6]) if len(p) > 6 else 0.0
                    phase = float(p[7]) if len(p) > 7 else 0.0

                    elems.append(VoltageSource(
                        a, b,
                        dc=dc, amp=amp, freq=freq,
                        phase_deg=phase, is_ac=True
                    ))
                else:
                    raise ValueError(f"Formato inválido para tensão: {p}")

                update_nodes(a, b)

            # ------------------ NON LINEAR RESISTOR ------------------
            elif element_type == "N":
                # Format: Nxxx a b V1 I1 V2 I2 V3 I3 V4 I4
                a = int(p[1]); b = int(p[2]) # Nodes
                V1 = float(p[3]); I1 = float(p[4])
                V2 = float(p[5]); I2 = float(p[6])
                V3 = float(p[7]); I3 = float(p[8])
                V4 = float(p[9]); I4 = float(p[10])
                elems.append(NonLinearResistor(a, b, np.array([V1, V2, V3, V4]), np.array([I1, I2, I3, I4])))
                update_nodes(a, b)
                
            # ------------------- DIODE -------------------
            elif element_type == "D":
                # Format: Dxxx a b
                a = int(p[1]); b = int(p[2])
                elems.append(Diode(a, b))
                update_nodes(a, b)

            # -----------------------------------------------------
            # FUTUROS ELEMENTOS (diode, opamp, mosfet, etc)
            # -----------------------------------------------------
            else:
                raise ValueError(f"Elemento não reconhecido: {p}")

    return NetlistOOP(elems, maxnode)
