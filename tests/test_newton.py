import numpy as np
import pytest

from simulator.engine import solve_tran, solve_dc
from simulator.parser import parse_netlist
from simulator.elements.base import TimeMethod


# ============================================================
# TESTE 1 — exemplo básico de transiente (example_tran.net)
# ============================================================
def test_example_tran_transient_runs():
    data = parse_netlist("circuits/example_tran.net")

    t, out = solve_tran(
        data,
        total_time=0.01,
        dt=1e-4,
        nr_tol=1e-6,
        v0_vector=None,
        desired_nodes=[1],
        method=TimeMethod.BACKWARD_EULER
    )

    v = out[0]

    # Verifica se não é tudo zero
    assert not np.allclose(v, 0), "example_tran.net gerou apenas zeros"

    # Deve ter pontos suficientes
    assert len(v) > 10


# ============================================================
# TESTE 2 — exemplo DC (example_dc.net)
# ============================================================
def test_example_dc_solve():
    data = parse_netlist("circuits/example_dc.net")

    out = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[1])

    assert isinstance(out, np.ndarray)
    assert out.size == 1
    assert not np.isnan(out[0])


# ============================================================
# TESTE 3 — divisor de tensão DC (vdc_divider.net)
# ============================================================
def test_vdc_divider_runs():
    data = parse_netlist("circuits/vdc_divider.net")

    out = solve_dc(data, nr_tol=1e-6, v0_vector=None, desired_nodes=[2])

    assert isinstance(out, np.ndarray)
    assert out.size == 1
    assert out[0] >= 0  # tensão não negativa


# ============================================================
# TESTE 4 — caso impossível (testa falha NR)
# ============================================================
def test_newton_fail():
    """
    Verifica se NR falha corretamente quando colocar uma netlist impossível.
    """
    impossible = """
* circuito impossível para NR
R1 1 0 1
V1 1 0 DC 5
R2 1 0 1
.end
"""
    with open("circuits/impossible.net", "w") as f:
        f.write(impossible)

    data = parse_netlist("circuits/impossible.net")

    with pytest.raises(RuntimeError):
        solve_tran(
            data,
            total_time=0.001,
            dt=1e-4,
            nr_tol=1e-12,
            v0_vector=None,
            desired_nodes=[1],
            method=TimeMethod.BACKWARD_EULER
        )
