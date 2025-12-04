from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np  # para NonLinearResistor

from .parser import NetlistOOP, TransientSettings

from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource
from .elements.nonlinear_resistor import NonLinearResistor
from .elements.diode import Diode

from pathlib import Path

@dataclass
class CircuitBuilder:
    # TODO: INIT ABLE TO RECEIVE NETLISTOOP AND CONTINUE CREATION
    name: str = "CIRCUITO_1"
    max_node: int = 0
    elements: List[object] = field(default_factory=list)
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
        self.elements.append(Resistor(a, b, R))
        self._update_max_node(a, b)

    def add_capacitor(self, a: int, b: int, C: float, ic: float = 0.0):
        """Capacitor: C <node a> <node b> <C> <ic>"""
        self.elements.append(Capacitor(a, b, C, ic))
        self._update_max_node(a, b)

    def add_inductor(self, a: int, b: int, L: float, ic: float = 0.0):
        """Inductor: L [<node a> <node b> <L> <ic>"""
        self.elements.append(Inductor(a, b, L, ic))
        self._update_max_node(a, b)

    # ------------- Current Sources --------------
    def add_current_source_dc(self, a: int, b: int, dc: float):
        """Current Source DC: I <node a> <node b> DC <dc>"""
        self.elements.append(CurrentSource(a, b, dc=dc, is_ac=False))
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
        self.elements.append(
            CurrentSource(
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
        self.elements.append(
            VoltageSource(a, b, dc=dc, is_ac=False, source_type="DC")
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
        self.elements.append(
            VoltageSource(
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
                a,
                b,
                dc=v1,  # valor de DC para análise DC
                source_type="PULSE",
                pulse_params=pulse_params,
            )
        )
        self._update_max_node(a, b)

    # ----------------- Non Linear Elements -----------------
    def add_nonlinear_resistor(
        self,
        a: int,
        b: int,
        V_points: list[float],
        I_points: list[float],
    ):
        """Non Linear Resistor: N <node a> <node b> <V1> <I1> <V2> <I2> <V3> <I3> <V4> <I4>"""
        if len(V_points) != 4 or len(I_points) != 4:
            raise ValueError("São necessários exatamente 4 pontos (V,I) para o resistor não-linear.")
        self.elements.append(
            NonLinearResistor(
                a,
                b,
                np.array(V_points, dtype=float),
                np.array(I_points, dtype=float),
            )
        )
        self._update_max_node(a, b)

    def add_diode(self, a: int, b: int):
        """Diode: D <node a> <node b>"""
        self.elements.append(Diode(a, b))
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

        # Contadores de nomes sintéticos
        r_count = c_count = l_count = i_count = v_count = d_count = nl_count = 0

        for elem in self.elements:
            # ----------------- RESISTOR -----------------
            if isinstance(elem, Resistor):
                r_count += 1
                name = f"R{r_count}"
                # Formato: Rname a b R
                lines.append(f"{name} {elem.a} {elem.b} {elem.R}")

            # ----------------- CAPACITOR -----------------
            elif isinstance(elem, Capacitor):
                c_count += 1
                name = f"C{c_count}"
                base = f"{name} {elem.a} {elem.b} {elem.C}"
                # Quinta palavra opcional: IC=<valor>
                if getattr(elem, "Ic", 0.0):
                    base += f" IC={elem.v0}"
                lines.append(base)

            # ----------------- INDUTOR -----------------
            elif isinstance(elem, Inductor):
                l_count += 1
                name = f"L{l_count}"
                base = f"{name} {elem.a} {elem.b} {elem.L}"
                if getattr(elem, "Ic", 0.0):
                    base += f" IC={elem.i0}"
                lines.append(base)

            # ----------------- FONTE DE CORRENTE -----------------
            elif isinstance(elem, CurrentSource):
                i_count += 1
                name = f"I{i_count}"
                # Aqui assumo que o caso mais comum é DC
                # Formato: Iname a b DC valor
                dc = getattr(elem, "dc", 0.0)
                is_ac = getattr(elem, "is_ac", False)
                if not is_ac:
                    lines.append(f"{name} {elem.a} {elem.b} DC {dc}")
                else:
                    # Extensível depois para SIN/PULSE/etc.
                    lines.append(f"* Fonte de corrente AC não suportada na exportação: {name}")

            # ----------------- FONTE DE TENSÃO -----------------
            elif isinstance(elem, VoltageSource):
                v_count += 1
                name = f"V{v_count}"
                dc = getattr(elem, "dc", 0.0)
                is_ac = getattr(elem, "is_ac", False)
                if not is_ac:
                    lines.append(f"{name} {elem.a} {elem.b} DC {dc}")
                else:
                    lines.append(f"* Fonte de tensão AC não suportada na exportação: {name}")

            # ----------------- RESISTOR NÃO LINEAR -----------------
            elif isinstance(elem, NonLinearResistor):
                nl_count += 1
                name = f"RN{nl_count}"
                # Especificação de netlist para esse cara ainda não está formalizada,
                # então deixo como comentário para não quebrar o parser.
                lines.append(f"* NonLinearResistor {name} {elem.a} {elem.b}")

            # ----------------- DIODO -----------------
            elif isinstance(elem, Diode):
                d_count += 1
                name = f"D{d_count}"
                # Formato: Dname a b
                lines.append(f"{name} {elem.a} {elem.b}")

            # ----------------- OUTROS -----------------
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
