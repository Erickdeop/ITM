from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .elements.resistor import Resistor
from .elements.capacitor import Capacitor
from .elements.inductor import Inductor
from .elements.current_source import CurrentSource
from .elements.voltage_source import VoltageSource

@dataclass
class NetlistOOP:
    elements: List[object]
    max_node: int

def parse_netlist(path: str) -> NetlistOOP:
    elems = []
    maxnode = 0
    with open(path, 'r') as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith('*'): continue
            p = s.split()
            k = p[0][0].upper()
            def up(*ns):
                nonlocal maxnode
                maxnode = max(maxnode, *ns)
            if k == 'R':
                a,b,val = int(p[1]), int(p[2]), float(p[3])
                elems.append(Resistor(a,b,val)); up(a,b)
            elif k == 'C':
                a,b,val = int(p[1]), int(p[2]), float(p[3])
                elems.append(Capacitor(a,b,val)); up(a,b)
            elif k == 'L':
                a,b,val = int(p[1]), int(p[2]), float(p[3])
                elems.append(Inductor(a,b,val)); up(a,b)
            elif k == 'I':
                a,b,stype = int(p[1]), int(p[2]), p[3].upper()
                dc = float(p[4])
                if stype == 'DC':
                    elems.append(CurrentSource(a,b,dc=dc,is_ac=False)); up(a,b)
                else:
                    amp,freq,phase = float(p[5]), float(p[6]), float(p[7])
                    elems.append(CurrentSource(a,b,dc=dc,amp=amp,freq=freq,phase_deg=phase,is_ac=True)); up(a,b)
            elif k == 'V':
                a,b,stype = int(p[1]), int(p[2]), p[3].upper()
                dc = float(p[4])
                if stype == 'DC':
                    elems.append(VoltageSource(a,b,dc=dc,is_ac=False)); up(a,b)
                else:
                    amp,freq,phase = float(p[5]), float(p[6]), float(p[7])
                    elems.append(VoltageSource(a,b,dc=dc,amp=amp,freq=freq,phase_deg=phase,is_ac=True)); up(a,b)
    return NetlistOOP(elems, maxnode)
