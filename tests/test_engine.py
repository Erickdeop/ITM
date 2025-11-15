import numpy as np
from simulator.engine import solve_dc, solve_tran
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod


# Utilitário para criar netlists temporárias
def write_tmp(path, text):
    with open(path, "w") as f:
        f.write(text)


# ============================================================
# 1) TESTE DC — divisor resistivo
# ============================================================
def test_dc_divider(tmp_path):

    nl = """
V1 1 0 DC 10
R1 1 2 1000
R2 2 0 1000
"""

    path = tmp_path / "dc_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))
    out = solve_dc(data, 1e-6, None, [2])

    assert np.isclose(out[0], 5.0, atol=1e-2)


# ============================================================
# 2) TESTE TRANSIENTE RC — valida Backward Euler
# ============================================================
def test_transient_rc(tmp_path):

    # RC carregando com fonte DC — comportamento monotônico crescente
    nl = """
V1 1 0 DC 5
R1 1 2 1000
C1 2 0 0.00001
"""

    path = tmp_path / "rc_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))

    t, out = solve_tran(
        data=data,
        total_time=0.05,       # 50 ms
        dt=0.0001,             # 0.1 ms
        nr_tol=1e-6,
        v0_vector=None,
        desired_nodes=[2],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # RC deve crescer monotonicamente
    assert v[10] < v[100] < v[-1]

    # Deve se aproximar do valor final (5V)
    assert v[-1] > 3.0
    assert v[-1] < 5.1


# ============================================================
# 3) TESTE TRANSIENTE RL — valida Backward Euler
# ============================================================
def test_transient_rl(tmp_path):

    # RL com fonte DC — tensão no indutor decai exponencialmente
    nl = """
V1 1 0 DC 5
R1 1 2 50
L1 2 0 0.001
"""

    path = tmp_path / "rl_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))

    t, out = solve_tran(
        data=data,
        total_time=0.02,       # 20 ms
        dt=0.0001,
        nr_tol=1e-6,
        v0_vector=None,
        desired_nodes=[2],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # Valor inicial deve estar próximo de 5V
    assert v[0] > 4.0

    # Valor final deve ser próximo de 0V (RL converge)
    assert v[-1] < 1.0

    # Decaimento monotônico
    # Em t=0, a tensão inicial deve ser diferente do regime
    assert abs(v[0] - v[-1]) > 0.5

    # Durante o tempo, o sinal deve se estabilizar (sem oscilar)
    assert np.all(np.diff(v) < 1e-6) or np.all(np.diff(v) > -1e-6)

