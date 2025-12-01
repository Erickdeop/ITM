import numpy as np
from simulator.engine import solve_dc, solve_tran
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod


def write_tmp(path, text):
    with open(path, "w") as f:
        f.write(text)


# ============================================================
# 1) TESTE DC — divisor resistivo
# ============================================================
def test_dc_divider(tmp_path):

    nl = """
2
V1 1 0 DC 10
R1 1 2 1000
R2 2 0 1000
"""

    path = tmp_path / "dc_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))

    v0 = np.zeros(data.max_node + 1)

    out = solve_dc(data, 1e-6, v0, [2])

    assert np.isclose(out[0], 5.0, atol=1e-2)


# ============================================================
# 2) TESTE TRANSIENTE RC — Backward Euler
# ============================================================
def test_transient_rc(tmp_path):

    nl = """
2
V1 1 0 DC 5
R1 1 2 1000
C1 2 0 0.00001
"""
    path = tmp_path / "rc_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))

    v0 = np.zeros(data.max_node + 1)

    t, out = solve_tran(
        data=data,
        total_time=0.05,
        dt=0.0001,
        nr_tol=1e-6,
        v0_vector=v0,
        desired_nodes=[2],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # comparar após alguns passos
    assert v[5] < v[50] < v[-1]

    # aproxima do final
    assert v[-1] > 3.0
    assert v[-1] < 5.1


# ============================================================
# 3) TESTE TRANSIENTE RL — Backward Euler
# ============================================================
def test_transient_rl(tmp_path):

    nl = """
2
V1 1 0 DC 5
R1 1 2 50
L1 2 0 0.001
"""

    path = tmp_path / "rl_test.cir"
    write_tmp(path, nl)

    data = parse_netlist(str(path))

    t, out = solve_tran(
        data=data,
        total_time=0.02,
        dt=0.0001,
        nr_tol=1e-6,
        v0_vector=np.zeros(data.max_node + 1),
        desired_nodes=[2],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # 1) há solução
    assert isinstance(v, np.ndarray)
    assert len(v) > 10

    # 2) o sinal não é constante
    assert not np.allclose(v, v[0])

    # 3) não explode para NaN ou inf
    assert np.all(np.isfinite(v))
