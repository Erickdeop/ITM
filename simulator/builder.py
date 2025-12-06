from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np  # para NonLinearResistor

from .parser import NetlistOOP, TransientSettings

from .elements.base import Element
from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource
from .elements.nonlinear_resistor import NonLinearResistor
from .elements.diode import Diode
from .elements.controlled_sources import VCVS, CCCS, VCCS, CCVS
from .elements.ampop import OpAmp

from pathlib import Path

@dataclass
class CircuitBuilder:
    # TODO: INIT ABLE TO RECEIVE NETLISTOOP AND CONTINUE CREATION
    name: str = "CIRCUITO_1"
    max_node: int = 0

    R_count: int = 0
    C_count: int = 0
    L_count: int = 0
    I_count: int = 0
    V_count: int = 0
    N_count: int = 0
    D_count: int = 0
    E_count: int = 0
    F_count: int = 0
    G_count: int = 0
    H_count: int = 0
    O_count: int = 0


    elements: List[Element] = field(default_factory=list)
    transient: TransientSettings = field(default_factory=TransientSettings)

    def rename(self, new_name: str):
        self.name = new_name

    def _update_max_node(self, *nodes: int):
        self.max_node = max(self.max_node, *nodes)

    # -----------------------------------------------------#
    #               ADD COMPONENT TO CIRCUIT               #
    # -----------------------------------------------------#

    # ----------------- Passive -----------------
    def add_resistor(self, a: int, b: int, R: float):
        """Resistor: R <node a> <node b> <R>"""
        self.R_count += 1
        self.elements.append(Resistor("R"+str(self.R_count), a, b, R))
        self._update_max_node(a, b)

    def add_capacitor(self, a: int, b: int, C: float, ic: float = 0.0):
        """Capacitor: C <node a> <node b> <C> <ic>"""
        self.C_count += 1
        self.elements.append(Capacitor("C"+str(self.C_count), a, b, C, ic))
        self._update_max_node(a, b)

    def add_inductor(self, a: int, b: int, L: float, ic: float = 0.0):
        """Inductor: L [<node a> <node b> <L> <ic>"""
        self.L_count += 1
        self.elements.append(Inductor("L"+str(self.L_count), a, b, L, ic))
        self._update_max_node(a, b)

    # ------------- Current Sources --------------
    def add_current_source_dc(self, a: int, b: int, dc: float):
        """Current Source DC: I <node a> <node b> DC <dc>"""
        self.I_count += 1
        self.elements.append(CurrentSource("I"+str(self.I_count), a, b, dc=dc, is_ac=False))
        self._update_max_node(a, b)

    def add_current_source_ac(
        self,
        a: int,
        b: int,
        dc: float = 0.0,
        amp: float = 0.0,
        freq: float = 0.0,
        phase_deg: float = 0.0,
    ):
        """Current Source AC: I <node a> <node b> AC <dc> <amp> <freq> <phase>"""
        self.I_count += 1
        self.elements.append(
            CurrentSource(
                "I"+str(self.I_count), 
                a,
                b,
                dc=dc,
                amp=amp,
                freq=freq,
                phase_deg=phase_deg,
                is_ac=True,
            )
        )
        self._update_max_node(a, b)

    # ----------------- Voltage Sources -----------------
    def add_voltage_source_dc(self, a: int, b: int, dc: float):
        """Voltage Source DC: V a b DC <dc>"""
        self.V_count += 1
        self.elements.append(
            VoltageSource("V"+str(self.V_count), a, b, dc=dc, is_ac=False, source_type="DC")
        )
        self._update_max_node(a, b)

    def add_voltage_source_ac(
        self,
        a: int,
        b: int,
        dc: float = 0.0,
        amp: float = 0.0,
        freq: float = 0.0,
        phase_deg: float = 0.0,
    ):
        """Voltage Source AC: V a b AC <dc> <amp> <freq> <phase>"""
        self.V_count += 1
        self.elements.append(
            VoltageSource(
                "V"+str(self.V_count), 
                a,
                b,
                dc=dc,
                amp=amp,
                freq=freq,
                phase_deg=phase_deg,
                is_ac=True,
                source_type="AC",
            )
        )
        self._update_max_node(a, b)

    def add_voltage_source_sin(
        self,
        a: int,
        b: int,
        offset: float = 0.0,
        amplitude: float = 0.0,
        freq: float = 0.0,
        delay: float = 0.0,
        damping: float = 0.0,
        phase_deg: float = 0.0,
    ):
        """Sin Voltage Source: V <node a> <node b> SIN <offset> <amplitude> <freq> <delay> <damping> <phase>"""
        self.V_count += 1
        sin_params = {
            "offset": offset,
            "amplitude": amplitude,
            "freq": freq,
            "delay": delay,
            "damping": damping,
            "phase": phase_deg,
        }
        self.elements.append(
            VoltageSource(
                "V"+str(self.V_count), 
                a,
                b,
                dc=offset,  # valor de DC para análise DC
                source_type="SIN",
                sin_params=sin_params,
            )
        )
        self._update_max_node(a, b)

    def add_voltage_source_pulse(
        self,
        a: int,
        b: int,
        v1: float = 0.0,
        v2: float = 0.0,
        delay: float = 0.0,
        rise_time: float = 0.0,
        fall_time: float = 0.0,
        pulse_width: float = 0.0,
        period: float = 0.0,
    ):
        """Pulse Voltage Source: V <node a> <node b> PULSE <v1> <v2> <delay> <rise> <fall> <width> <period>"""
        self.V_count += 1
        pulse_params = {
            "v1": v1,
            "v2": v2,
            "delay": delay,
            "rise_time": rise_time,
            "fall_time": fall_time,
            "pulse_width": pulse_width,
            "period": period,
        }
        self.elements.append(
            VoltageSource(
                "V"+str(self.V_count), 
                a,
                b,
                dc=v1,  # valor de DC para análise DC
                source_type="PULSE",
                pulse_params=pulse_params,
            )
        )
        self._update_max_node(a, b)

    # ----------------- Controlled Sources -----------------
    def add_vcvs(self, a: int, b: int, c: int, d: int, gain: float):
        """VCVS: E <n+> <n-> <nc+> <nc-> <gain>"""
        self.E_count += 1
        self.elements.append(VCVS("E"+str(self.E_count), a, b, c, d, gain))
        self._update_max_node(a, b, c, d)

    def add_cccs(self, a: int, b: int, c: int, d: int, gain: float):
        """CCCS: F <n+> <n-> <nc+> <nc-> <gain>"""
        self.F_count += 1
        self.elements.append(CCCS("F"+str(self.F_count), a, b, c, d, gain))
        self._update_max_node(a, b, c, d)

    def add_vccs(self, a: int, b: int, c: int, d: int, gm: float):
        """VCCS: G <n+> <n-> <nc+> <nc-> <gm>"""
        self.G_count += 1
        self.elements.append(VCCS("G"+str(self.G_count), a, b, c, d, gm))
        self._update_max_node(a, b, c, d)

    def add_ccvs(self, a: int, b: int, c: int, d: int, rm: float):
        """CCVS: H <n+> <n-> <nc+> <nc-> <rm>"""
        self.H_count += 1
        self.elements.append(CCVS("H"+str(self.H_count), a, b, c, d, rm))
        self._update_max_node(a, b, c, d)

    # ------------------------- AmpOp -----------------------
    def add_opamp(self, vp: int, vn: int, vo: int, gain: float = 1e5):
        """OpAmp ideal: O <vp> <vn> <vo> [gain]"""
        self.O_count += 1
        self.elements.append(
            OpAmp(
                "O"+str(self.O_count), 
                a=vo,   # Out +
                b=0,    # Out -
                c=vp,   # In +
                d=vn,   # In -
                gain=gain,
            )
        )
        self._update_max_node(vp, vn, vo)


    # ----------------- Non Linear Elements -----------------
    def add_nonlinear_resistor(
        self,
        a: int,
        b: int,
        V_points: list[float],
        I_points: list[float],
    ):
        """Non Linear Resistor: N <node a> <node b> <V1> <I1> <V2> <I2> <V3> <I3> <V4> <I4>"""
        self.R_count += 1
        if len(V_points) != 4 or len(I_points) != 4:
            raise ValueError("São necessários exatamente 4 pontos (V,I) para o resistor não-linear.")
        self.elements.append(
            NonLinearResistor(
                "N"+str(self.R_count), 
                a,
                b,
                np.array(V_points, dtype=float),
                np.array(I_points, dtype=float),
            )
        )
        self._update_max_node(a, b)

    def add_diode(self, a: int, b: int):
        """Diode: D <node a> <node b>"""
        self.R_count += 1
        self.elements.append(Diode("D"+str(self.R_count), a, b))
        self._update_max_node(a, b)


    # -----------------------------------------------------#
    #                   REMOVE COMPONENT                   #
    # -----------------------------------------------------#
    def remove_component(self, index: int) -> bool:
        """
        Remove um componente pelo índice (1-based).
        Retorna True se removeu, False se o índice for inválido.
        """
        if index < 1 or index > len(self.elements):
            return False

        self.elements.pop(index - 1)

        # Recalcula max_node com base nos elementos restantes
        if self.elements:
            self.max_node = max(
                max(getattr(e, "a", 0), getattr(e, "b", 0)) for e in self.elements
            )
        else:
            self.max_node = 0

        return True

    # -----------------------------------------------------#
    #                  SIMULATION CONFIGS                  #
    # -----------------------------------------------------#
    def set_transient(
        self,
        t_stop: float,
        dt: float,
        method: str = "BE",
        internal_steps: int = 1,
        uic: bool = True,
    ):
        self.transient.t_stop = t_stop
        self.transient.dt = dt
        self.transient.method = method.upper()
        self.transient.intetnal_steps = internal_steps
        self.transient.uic = uic

    def enable_transient(self, enabled: bool = True):
        self.transient.enabled = enabled


    # -----------------------------------------------------#
    #                   SAVE NETLIST                       #
    # -----------------------------------------------------#
    def save_netlist(self, file_path: str) -> None:
        """
        Salva o circuito atual em formato .net seguindo as especificações do trabalho:
        - 1ª linha: número de nós (max_node)
        - Linhas seguintes: um elemento por linha (R, C, L, I, V, D, etc.)
        - Última linha (se transiente habilitado): .TRAN ...
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []

        # 1ª linha: número de nós do circuito
        lines.append(str(self.max_node))

        for elem in self.elements:
            # ----------------- RESISTOR -----------------
            if isinstance(elem, Resistor):
                # Formato: Rname a b R
                lines.append(f"{elem.name} {elem.a} {elem.b} {elem.R}")

            # ----------------- CAPACITOR -----------------
            elif isinstance(elem, Capacitor):
                base = f"{elem.name} {elem.a} {elem.b} {elem.C}"
                # Quinta palavra opcional: IC=<valor>
                if getattr(elem, "Ic", 0.0):
                    base += f" IC={elem.v0}"
                lines.append(base)

            # ----------------- INDUTOR -----------------
            elif isinstance(elem, Inductor):
                base = f"{elem.name} {elem.a} {elem.b} {elem.L}"
                if getattr(elem, "Ic", 0.0):
                    base += f" IC={elem.i0}"
                lines.append(base)

 # ----------------- FONTE DE CORRENTE -----------------
            elif isinstance(elem, CurrentSource):
                # Formatos suportados:
                # Iname a b DC <dc>
                # Iname a b AC <dc> <amp> <freq> <phase>
                # Iname a b SIN <offset> <amplitude> <freq> <delay> <damping> <phase>
                # Iname a b PULSE <i1> <i2> <delay> <rise> <fall> <width> <period>
                stype = getattr(elem, "source_type", "DC").upper()

                if stype == "DC":
                    dc = getattr(elem, "dc", 0.0)
                    lines.append(f"{elem.name} {elem.a} {elem.b} DC {dc}")

                elif stype == "AC":
                    dc = getattr(elem, "dc", 0.0)
                    amp = getattr(elem, "amp", 0.0)
                    freq = getattr(elem, "freq", 0.0)
                    phase = getattr(elem, "phase_deg", 0.0)
                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} AC {dc} {amp} {freq} {phase}"
                    )

                elif stype == "SIN":
                    params = getattr(elem, "sin_params", {}) or {}
                    offset    = params.get("offset",    getattr(elem, "dc", 0.0))
                    amplitude = params.get("amplitude", getattr(elem, "amp", 0.0))
                    freq      = params.get("freq",      getattr(elem, "freq", 0.0))
                    delay     = params.get("delay",     0.0)
                    damping   = params.get("damping",   0.0)
                    phase     = params.get("phase",     getattr(elem, "phase_deg", 0.0))

                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} SIN "
                        f"{offset} {amplitude} {freq} {delay} {damping} {phase}"
                    )

                elif stype == "PULSE":
                    params = getattr(elem, "pulse_params", {}) or {}
                    i1          = params.get("i1", getattr(elem, "dc", 0.0))
                    i2          = params.get("i2", getattr(elem, "amp", 0.0))
                    delay       = params.get("delay", 0.0)
                    rise_time   = params.get("rise_time", 0.0)
                    fall_time   = params.get("fall_time", 0.0)
                    pulse_width = params.get("pulse_width", 0.0)
                    period      = params.get("period", 0.0)

                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} PULSE "
                        f"{i1} {i2} {delay} {rise_time} {fall_time} {pulse_width} {period}"
                    )

                else:
                    lines.append(
                        f"* Fonte de corrente com tipo desconhecido: "
                        f"{elem.name} (source_type={stype})"
                    )

            # ----------------- FONTE DE TENSÃO -----------------
            elif isinstance(elem, VoltageSource):
                # Formatos suportados:
                # Vname a b DC <dc>
                # Vname a b AC <dc> <amp> <freq> <phase>
                # Vname a b SIN <offset> <amplitude> <freq> <delay> <damping> <phase>
                # Vname a b PULSE <v1> <v2> <delay> <rise> <fall> <width> <period>
                stype = getattr(elem, "source_type", "DC").upper()

                if stype == "DC":
                    dc = getattr(elem, "dc", 0.0)
                    lines.append(f"{elem.name} {elem.a} {elem.b} DC {dc}")

                elif stype == "AC":
                    dc = getattr(elem, "dc", 0.0)
                    amp = getattr(elem, "amp", 0.0)
                    freq = getattr(elem, "freq", 0.0)
                    phase = getattr(elem, "phase_deg", 0.0)
                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} AC {dc} {amp} {freq} {phase}"
                    )

                elif stype == "SIN":
                    params = getattr(elem, "sin_params", {}) or {}
                    offset    = params.get("offset",    getattr(elem, "dc", 0.0))
                    amplitude = params.get("amplitude", getattr(elem, "amp", 0.0))
                    freq      = params.get("freq",      getattr(elem, "freq", 0.0))
                    delay     = params.get("delay",     0.0)
                    damping   = params.get("damping",   0.0)
                    phase     = params.get("phase",     getattr(elem, "phase_deg", 0.0))

                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} SIN "
                        f"{offset} {amplitude} {freq} {delay} {damping} {phase}"
                    )

                elif stype == "PULSE":
                    params = getattr(elem, "pulse_params", {}) or {}
                    v1          = params.get("v1", getattr(elem, "dc", 0.0))
                    v2          = params.get("v2", getattr(elem, "amp", 0.0))
                    delay       = params.get("delay", 0.0)
                    rise_time   = params.get("rise_time", 0.0)
                    fall_time   = params.get("fall_time", 0.0)
                    pulse_width = params.get("pulse_width", 0.0)
                    period      = params.get("period", 0.0)

                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} PULSE "
                        f"{v1} {v2} {delay} {rise_time} {fall_time} {pulse_width} {period}"
                    )

                else:
                    lines.append(
                        f"* Fonte de tensão com tipo desconhecido: "
                        f"{elem.name} (source_type={stype})"
                    )

            # ----------------- RESISTOR NÃO LINEAR -----------------
            elif isinstance(elem, NonLinearResistor):
                # Formato: Nname a b V1 I1 V2 I2 V3 I3 V4 I4
                V_pts = list(getattr(elem, "V_points", []))
                I_pts = list(getattr(elem, "I_points", []))

                if len(V_pts) == 4 and len(I_pts) == 4:
                    lines.append(
                        f"{elem.name} {elem.a} {elem.b} "
                        f"{V_pts[0]} {I_pts[0]} "
                        f"{V_pts[1]} {I_pts[1]} "
                        f"{V_pts[2]} {I_pts[2]} "
                        f"{V_pts[3]} {I_pts[3]}"
                    )
                else:
                    # Caso algo esteja inconsistente, não quebra o arquivo.
                    lines.append(
                        f"* NonLinearResistor mal definido: "
                        f"{elem.name} {elem.a} {elem.b} (esperados 4 pontos)"
                    )

            # ----------------- DIODO -----------------
            elif isinstance(elem, Diode):
                # Formato: Dname a b
                lines.append(f"{elem.name} {elem.a} {elem.b}")

             # ----------------- FONTES CONTROLADAS E OPAMP -----------------
            elif isinstance(elem, VCVS):
                # VCVS: Ename a b c d gain
                lines.append(
                    f"{elem.name} {elem.a} {elem.b} {elem.c} {elem.d} {elem.gain}"
                )

            elif isinstance(elem, CCCS):
                # CCCS: Fname a b c d gain
                lines.append(
                    f"{elem.name} {elem.a} {elem.b} {elem.c} {elem.d} {elem.gain}"
                )

            elif isinstance(elem, VCCS):
                # VCCS: Gname a b c d gm
                lines.append(
                    f"{elem.name} {elem.a} {elem.b} {elem.c} {elem.d} {elem.gm}"
                )

            elif isinstance(elem, CCVS):
                # CCVS: Hname a b c d rm
                lines.append(
                    f"{elem.name} {elem.a} {elem.b} {elem.c} {elem.d} {elem.rm}"
                )

            elif isinstance(elem, OpAmp):
                # Amplificador operacional ideal:
                # O name vp vn vo
                vp = elem.c   # entrada não inversora
                vn = elem.d   # entrada inversora
                vo = elem.a   # saída
                lines.append(f"{elem.name} {vp} {vn} {vo}")
            else:
                # Não impede salvar o arquivo, só documenta o elemento
                lines.append(f"* Elemento não suportado na exportação: {elem}")

        # ----------------- LINHA .TRAN (se transiente habilitado) -----------------
        if self.transient.enabled:
            t_stop = self.transient.t_stop
            dt = self.transient.dt
            method = self.transient.method.upper()
            internal_steps = self.transient.intetnal_steps

            tran_line = f".TRAN {t_stop} {dt} {method} {internal_steps}"
            if self.transient.uic:
                tran_line += " UIC"
            lines.append(tran_line)

        # Escreve arquivo
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


    # -----------------------------------------------------#
    #                 TO NETLIST OBJECT                    #
    # -----------------------------------------------------#
    def to_netlist_oop(self) -> NetlistOOP:
        return NetlistOOP(
            elements=self.elements.copy(),
            max_node=self.max_node,
            transient=self.transient,
        )
