import numpy as np
from simulator.parser import parse_netlist
from simulator.elements.opamp import OpAmp
from simulator.engine import solve_dc


def test_parser_reads_ideal_opamp(tmp_path):
    net_text = """3
O9901 0 2 3
.TRAN 0.001 1e-04 BE 1
"""
    net_path = tmp_path / "opamp_unit.net"
    net_path.write_text(net_text)

    netlist = parse_netlist(str(net_path))
    print(netlist)  # só pra debug se quiser

    # pega elementos cuja classe se chama "OpAmp", independente do módulo
    opamps = [e for e in netlist.elements if e.__class__.__name__ == "OpAmp"]
    assert len(opamps) == 1

    op = opamps[0]

    # Especificação: Oxxxx vp vn vo
    # parser: a=vo, b=0, c=vp, d=vn, gain=1e5
    assert op.a == 3      # saída +
    assert op.b == 0      # saída -
    assert op.c == 0      # entrada +
    assert op.d == 2      # entrada -
    assert op.gain == 1e5

def test_opamp_dc_follower_virtual_short(tmp_path):
    # Agora usamos nós 0, 1, 2 e max_node=2
    net_text = """2
V1 1 0 DC 1
R1 2 0 1000
O1 1 2 2
.TRAN 0.001 1e-04 BE 1
"""
    net_path = tmp_path / "opamp_dc.net"
    net_path.write_text(net_text)

    data = parse_netlist(str(net_path))

    desired_nodes = [1, 2]

    v = solve_dc(
        data=data,
        nr_tol=1e-8,
        v0_vector=None,
        desired_nodes=desired_nodes,
    )

    v_in, v_out = v  # nós 1 e 2

    # virtual short: v+ ≈ v− => v_in ≈ v_out
    assert abs(v_out - v_in) < 1e-3
