from __future__ import annotations
import numpy as np

from .circuit import TransientSettings, NetlistOOP

from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource
from .elements.nonlinear_resistor import NonLinearResistor
from .elements.diode import Diode
from .elements.controlled_sources import VCVS, CCCS, VCCS, CCVS
from .elements.ampop import OpAmp

def _parse_ic_token(token: str) -> float:
    token = token.strip()
    if token.upper().startswith("IC="):
        token = token.split("=", 1)[1]
    return float(token)

def parse_netlist(path: str) -> NetlistOOP:
    elems = []
    maxnode = 0
    ts = TransientSettings()

    with open(path, "r") as f:
        # --------- GET MAX NODES ---------
        for raw in f:
            line = raw.strip()

            if not line or line.startswith("*"):
                continue
            try:
                maxnode = int(line)
            except ValueError:
                raise ValueError(
                    f"\033[31mNo Max Nodes:\33[0m A primeira linha válida da netlist deve ser um inteiro "
                    f"com o número máximo de nós. Recebido: {line!r}"
                )
            break

        if maxnode is None or maxnode <= 0:
            raise ValueError("\033[31mNo Netlist:\33[0m Netlist vazia ou sem linha de número de nós.")

        for raw in f:
            line = raw.strip()

            if not line or line.startswith("*"):
                continue

            p = line.split()
            element_type = p[0][0].upper()
            element_name = p[0]
            # ---------------- SET TRANSIENT -----------------
            if line.startswith("."):
                if len(p) < 5:
                        raise ValueError("\033[31mIncomplete Transient settings:\33[0m Linha .TRAN"
                                         " requer pelo menos 5 argumentos no seguinte formato: "
                                         "\n .TRAN <tstop> <dt> <method> <internal_steps> [UIC]")
                ts = TransientSettings(
                    enabled = True,
                    t_stop = float(p[1]),
                    dt = float(p[2]),
                    method = p[3].upper(),
                    intetnal_steps = int(p[4])
                    )
                # When not use UIC?
            # ------------------- RESISTOR -------------------
            elif element_type == "R":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                elems.append(Resistor(element_name, a, b, val))

            # ------------------- CAPACITOR -------------------
            elif element_type == "C":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                ic = _parse_ic_token(p[4]) if len(p) > 4 else 0.0
                elems.append(Capacitor(element_name, a, b, val, ic))

            # ------------------- INDUCTOR -------------------
            elif element_type == "L":
                a = int(p[1]); b = int(p[2]); val = float(p[3])
                ic = _parse_ic_token(p[4]) if len(p) > 4 else 0.0
                elems.append(Inductor(element_name, a, b, val, ic))

            # ------------------- CURRENT SOURCE -------------------
            elif element_type == "I":
                a = int(p[1]); b = int(p[2])
                stype = p[3].upper()

                if stype == "DC":
                    dc = float(p[4])
                    elems.append(CurrentSource(element_name, a, b, dc=dc, is_ac=False))

                elif stype == "AC":
                    dc = float(p[4]) if len(p) > 4 else 0.0
                    amp = float(p[5]) if len(p) > 5 else 0.0
                    freq = float(p[6]) if len(p) > 6 else 0.0
                    phase = float(p[7]) if len(p) > 7 else 0.0

                    elems.append(CurrentSource(
                        element_name, a, b,
                        dc=dc, amp=amp, freq=freq,
                        phase_deg=phase, is_ac=True
                    ))
                else:
                    raise ValueError(f"\033[31mInvalid Format:\33[0m Formato inválido para corrente: {p}")

            # ------------------- VOLTAGE SOURCE -------------------
            elif element_type == "V":
                a = int(p[1]); b = int(p[2])
                stype = p[3].upper()

                if stype == "DC":
                    dc = float(p[4])
                    elems.append(VoltageSource(element_name, a, b, 
                                               dc=dc, is_ac=False, source_type="DC"))

                elif stype == "AC":
                    dc = float(p[4]) if len(p) > 4 else 0.0
                    amp = float(p[5]) if len(p) > 5 else 0.0
                    freq = float(p[6]) if len(p) > 6 else 0.0
                    phase = float(p[7]) if len(p) > 7 else 0.0

                    elems.append(VoltageSource(
                        element_name, a, b,
                        dc=dc, amp=amp, freq=freq,
                        phase_deg=phase, is_ac=True, source_type="AC"
                    ))

                elif stype == "SIN":
                    offset = float(p[4]) if len(p) > 4 else 0.0
                    amplitude = float(p[5]) if len(p) > 5 else 0.0
                    freq = float(p[6]) if len(p) > 6 else 0.0
                    delay = float(p[7]) if len(p) > 7 else 0.0
                    damping = float(p[8]) if len(p) > 8 else 0.0
                    phase = float(p[9]) if len(p) > 9 else 0.0
                    
                    sin_params = {
                        "offset": offset,
                        "amplitude": amplitude,
                        "freq": freq,
                        "delay": delay,
                        "damping": damping,
                        "phase": phase
                    }
                    
                    elems.append(VoltageSource(
                        element_name, a, b,
                        dc=offset,  # DC analysis
                        source_type="SIN",
                        sin_params=sin_params
                    ))

                elif stype == "PULSE":
                    v1 = float(p[4]) if len(p) > 4 else 0.0
                    v2 = float(p[5]) if len(p) > 5 else 0.0
                    delay = float(p[6]) if len(p) > 6 else 0.0
                    rise_time = float(p[7]) if len(p) > 7 else 0.0
                    fall_time = float(p[8]) if len(p) > 8 else 0.0
                    pulse_width = float(p[9]) if len(p) > 9 else 0.0
                    period = float(p[10]) if len(p) > 10 else 0.0
                    
                    pulse_params = {
                        "v1": v1,
                        "v2": v2,
                        "delay": delay,
                        "rise_time": rise_time,
                        "fall_time": fall_time,
                        "pulse_width": pulse_width,
                        "period": period
                    }
                    
                    elems.append(VoltageSource(
                        element_name, a, b,
                        dc=v1,  # DC analysis
                        source_type="PULSE",
                        pulse_params=pulse_params
                    ))

                else:
                    raise ValueError(f"\033[31mInvalid Format:\33[0m Formato inválido para tensão: {p}")

            # ------------------ NON LINEAR RESISTOR ------------------
            elif element_type == "N":
                # Format: Nxxx a b V1 I1 V2 I2 V3 I3 V4 I4
                a = int(p[1]); b = int(p[2]) # Nodes
                V1 = float(p[3]); I1 = float(p[4])
                V2 = float(p[5]); I2 = float(p[6])
                V3 = float(p[7]); I3 = float(p[8])
                V4 = float(p[9]); I4 = float(p[10])
                elems.append(NonLinearResistor(
                    element_name, a, b, 
                    np.array([V1, V2, V3, V4]), 
                    np.array([I1, I2, I3, I4])
                    ))
                
            # ------------------- DIODE -------------------
            elif element_type == "D":
                # Format: Dxxx a b
                a = int(p[1]); b = int(p[2])
                elems.append(Diode(element_name, a, b))

            # ------------------- VCVS (E) -------------------
            elif element_type == "E":
                # Format: Exxx n+ n- nc+ nc- gain
                a = int(p[1])     # output positive
                b = int(p[2])     # output negative
                c = int(p[3])     # control positive
                d = int(p[4])     # control negative
                gain = float(p[5])
                elems.append(VCVS(element_name, a, b, c, d, gain))

            # ------------------- CCCS (F) -------------------
            elif element_type == "F":
                # Format: Fxxx n+ n- nc+ nc- gain
                a = int(p[1])     # output positive
                b = int(p[2])     # output negative
                c = int(p[3])     # control positive
                d = int(p[4])     # control negative
                gain = float(p[5])
                elems.append(CCCS(element_name, a, b, c, d, gain))

            # ------------------- VCCS (G) -------------------
            elif element_type == "G":
                # Format: Gxxx n+ n- nc+ nc- gm
                a = int(p[1])     # output positive
                b = int(p[2])     # output negative
                c = int(p[3])     # control positive
                d = int(p[4])     # control negative
                gm = float(p[5])  # transconductance
                elems.append(VCCS(element_name, a, b, c, d, gm))

            # ------------------- CCVS (H) -------------------
            elif element_type == "H":
                # Format: Hxxx n+ n- nc+ nc- rm
                a = int(p[1])     # output positive
                b = int(p[2])     # output negative
                c = int(p[3])     # control positive
                d = int(p[4])     # control negative
                rm = float(p[5])  # transresistance
                elems.append(CCVS(element_name, a, b, c, d, rm))

             # ------------------- OPAMP (O) -------------------
            elif element_type == "O":
                if len(p) < 4:
                    raise ValueError(
                        f"\033[31mInvalid Format:\33[0m "
                        f"Opamp ideal requer: Oxxxx vp vn vo. Recebido: {p}"
                    )

                vp = int(p[1])   # nó de controle positivo (v+)
                vn = int(p[2])   # nó de controle negativo (v-)
                vo = int(p[3])   # nó de saída

                gain = 1e5  # ganho bem alto (opamp ideal)

                # Usando nossa classe OpAmp como VCVS de ganho alto,
                # single-ended com saída referenciada ao terra (0).
                elems.append(
                    OpAmp(
                        element_name, 
                        a=vo,      # saída +
                        b=0,       # saída - presa no GND
                        c=vp,      # entrada +
                        d=vn,      # entrada -
                        gain=gain,
                    )
                )
            # -----------------------------------------------------
            # FUTUROS ELEMENTOS (opamp, mosfet, etc)
            # -----------------------------------------------------
            else:
                raise ValueError(f"\033[31mNo Matching Element:\33[0m Elemento não reconhecido: {p}")

    # Detect if circuit has nonlinear elements
    has_nonlinear = any(getattr(elem, 'is_nonlinear', False) for elem in elems)
    
    nl = NetlistOOP(elems, maxnode, ts, has_nonlinear)
    if has_nonlinear:
        print("Circuit contains NONLINEAR elements - Newton-Raphson will be used")
    else:
        print("Circuit contains only LINEAR elements - Direct solve will be used")
    return nl

